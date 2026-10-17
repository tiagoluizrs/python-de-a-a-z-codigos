"""Herança simples: sobrescrever, estender com super() e a armadilha do __init__."""


class Animal:
    sound = "..."

    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} faz {self.sound}"

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"


class Dog(Animal):
    sound = "au"                       # sobrescreve o atributo da classe

    def __init__(self, name, tricks=()):
        super().__init__(name)         # reaproveita a inicialização da base
        self.tricks = list(tricks)

    def speak(self):                   # ESTENDE: usa o da base e acrescenta
        base = super().speak()
        return f"{base}!" if not self.tricks else f"{base}! (e sabe {self.tricks[0]})"


rex = Dog("Rex", ["sentar"])
print(rex, "|", rex.speak())
print(Animal("Gato").speak())
print(isinstance(rex, Dog), isinstance(rex, Animal), type(rex) is Animal)
print(issubclass(Dog, Animal), issubclass(Animal, Dog), issubclass(Dog, object))
print(Dog.__bases__, Dog.__mro__)
print(Animal.__subclasses__())


# Armadilha: esquecer o super().__init__()
class Cat(Animal):
    def __init__(self, name):
        self.lives = 9                 # esqueceu de chamar super().__init__


try:
    Cat("Tom").speak()
except AttributeError as error:
    print("AttributeError:", error)


# Chamar a base por nome funciona, mas não coopera com herança múltipla
class Puppy(Dog):
    def __init__(self, name):
        Dog.__init__(self, name)       # acoplado ao nome da classe
        self.age = 0


print(Puppy("Bob").age, Puppy("Bob").speak())
