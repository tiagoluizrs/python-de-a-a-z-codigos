"""O protocolo do descritor: __get__, __set__, __delete__, __set_name__."""


class Verbose:
    """Descritor de DADOS (tem __set__): imprime tudo que acontece."""

    def __set_name__(self, owner, name):
        self.name = name
        print(f"  __set_name__(owner={owner.__name__}, name={name!r})")

    def __get__(self, obj, objtype=None):
        print(f"  __get__(obj={'None' if obj is None else 'instância'}, "
              f"objtype={objtype.__name__})")
        if obj is None:
            return self                          # acesso pela classe
        return obj.__dict__.get("_" + self.name, "<vazio>")

    def __set__(self, obj, value):
        print(f"  __set__({value!r})")
        obj.__dict__["_" + self.name] = value

    def __delete__(self, obj):
        print("  __delete__")
        obj.__dict__.pop("_" + self.name, None)


class Model:
    field = Verbose()                            # __set_name__ roda AQUI, na definição


m = Model()
print("m.field = 1"); m.field = 1
print("m.field"); print("  =>", m.field)
print("Model.field"); print("  =>", type(Model.field).__name__)
print("del m.field"); del m.field


# Precedência: descritor de dados > __dict__ da instância > descritor sem dados / atributo de classe
class DataDesc:
    def __get__(self, obj, objtype=None):
        return "do descritor de DADOS"

    def __set__(self, obj, value):
        pass


class NonDataDesc:
    def __get__(self, obj, objtype=None):
        return "do descritor SEM dados"


class Demo:
    data = DataDesc()
    nondata = NonDataDesc()
    plain = "atributo de classe"


d = Demo()
d.__dict__["data"] = "no dict da instância"
d.__dict__["nondata"] = "no dict da instância"
d.__dict__["plain"] = "no dict da instância"
print(d.data)        # o descritor de dados vence o dict
print(d.nondata)     # o dict vence o descritor sem dados
print(d.plain)       # o dict vence o atributo de classe
print(type(d).__mro__[0].__dict__["data"].__class__.__name__)
