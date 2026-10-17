"""Métodos de instância, de classe e estáticos."""
import datetime as dt


class Temperature:
    SCALES = {"C", "F", "K"}

    def __init__(self, celsius):
        self.celsius = celsius

    # --- classmethod: construtores alternativos; recebe a CLASSE
    @classmethod
    def from_fahrenheit(cls, fahrenheit):
        return cls((fahrenheit - 32) * 5 / 9)

    @classmethod
    def from_kelvin(cls, kelvin):
        return cls(kelvin - 273.15)

    # --- staticmethod: função organizada dentro da classe; sem self nem cls
    @staticmethod
    def is_valid_scale(scale):
        return scale in Temperature.SCALES

    # --- método de instância
    def to_fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    def __repr__(self):
        return f"{type(self).__name__}({self.celsius:.2f})"


print(Temperature.from_fahrenheit(212), Temperature.from_kelvin(300))
print(Temperature.is_valid_scale("K"), Temperature(100).to_fahrenheit())


# O classmethod respeita subclasses: `cls` é a subclasse
class Precise(Temperature):
    pass


print(Precise.from_kelvin(0), type(Precise.from_kelvin(0)).__name__)


# Como funcionam: funções na classe viram métodos ligados no acesso
t = Temperature(10)
print(t.to_fahrenheit, "|", Temperature.to_fahrenheit)
print(t.to_fahrenheit.__self__ is t, t.to_fahrenheit.__func__ is Temperature.to_fahrenheit)
print(Temperature.to_fahrenheit(t) == t.to_fahrenheit())

# Uma função atribuída à INSTÂNCIA não vira método (não recebe self)
t.shout = lambda: "sem self"
print(t.shout())
Temperature.shout2 = lambda self: f"com self: {self.celsius}"     # na CLASSE vira método
print(t.shout2())

# Atributo que é callable e não função: não faz a ligação
class Handler:
    callback = print                       # builtin: não é descritor de método
    function = lambda self: "ligada"       # função: vira método


print(Handler().function())
Handler().callback("o print não recebeu o self")
