"""property: atributos que parecem simples, mas têm lógica."""


class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius                   # passa pelo setter (validação)

    @property
    def celsius(self):
        """Temperatura em graus Celsius."""
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("abaixo do zero absoluto")
        self._celsius = value

    @property
    def fahrenheit(self):                        # calculada, somente leitura
        return self._celsius * 9 / 5 + 32

    @celsius.deleter
    def celsius(self):
        print("  apagando celsius")
        del self._celsius


t = Temperature(100)
print(t.celsius, t.fahrenheit)
t.celsius = 0
print(t.celsius, t.fahrenheit)
for action, label in ((lambda: setattr(t, "celsius", -300), "valor inválido"),
                      (lambda: setattr(t, "fahrenheit", 50), "somente leitura")):
    try:
        action()
    except (ValueError, AttributeError) as error:
        print(f"{label}: {type(error).__name__}: {error}")
del t.celsius
print(Temperature.celsius.__doc__)
print(type(Temperature.celsius), type(Temperature.__dict__["celsius"]))
print(Temperature.celsius is Temperature.__dict__["celsius"])     # acessar pela classe devolve a property
print(vars(Temperature(5)))                                        # só _celsius está na instância


# A sintaxe @property é açúcar para property(fget, fset, fdel, doc)
class Manual:
    def _get(self):
        return self._v

    def _set(self, value):
        self._v = value * 2

    v = property(_get, _set, doc="dobra ao gravar")


m = Manual()
m.v = 21
print(m.v, Manual.v.__doc__)
