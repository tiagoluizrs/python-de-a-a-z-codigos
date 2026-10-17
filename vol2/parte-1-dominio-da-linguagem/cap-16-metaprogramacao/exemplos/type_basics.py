"""Classes são objetos: type() cria classes; a instrução class é açúcar."""
import dis

# 1) type(nome, bases, namespace) cria uma classe
def greet(self):
    return f"oi, {self.name}"


Person = type("Person", (object,), {"species": "human", "greet": greet,
                                     "__init__": lambda self, name: setattr(self, "name", name)})
p = Person("Ana")
print(p.greet(), Person.species, Person.__name__, type(Person), type(p) is Person)


# 2) a instrução class faz o mesmo (mas a sintaxe é mais legível)
class Person2:
    species = "human"

    def __init__(self, name):
        self.name = name

    greet = greet


print(Person2("Bia").greet(), type(Person2))

# 3) por baixo: __build_class__ executa o corpo e chama a metaclasse
code = compile("class K:\n    x = 1\n", "<demo>", "exec")
print([i.opname for i in dis.get_instructions(code) if "BUILD" in i.opname or "CLASS" in i.opname])

# 4) quem cria as classes? type; e quem cria o type? ele mesmo
print(type(int), type(type), isinstance(type, object), isinstance(object, type))
print(Person.__mro__, Person.__bases__, Person.__dict__["species"])

# 5) classes são mutáveis: dá para acrescentar métodos depois
Person.shout = lambda self: self.name.upper()
print(p.shout())                                       # instâncias existentes enxergam

# 6) __prepare__: o namespace do corpo pode ser outro mapeamento
class Meta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        print("__prepare__ chamado para", name)
        return {}                                      # poderia ser um dict especial


class WithMeta(metaclass=Meta):
    a = 1
