"""Como o super() sem argumentos sabe quem é quem."""


class A:
    def who(self):
        return "A"

    @classmethod
    def make(cls):
        return f"A.make({cls.__name__})"


class B(A):
    def who(self):
        # super() sem argumentos usa a célula __class__ e o primeiro parâmetro
        return "B>" + super().who()

    @classmethod
    def make(cls):
        return "B>" + super().make()


print(B().who(), "|", B.make())
print(B.who.__code__.co_freevars)             # ('__class__',): a classe onde o método nasceu
print(B.who.__closure__[0].cell_contents is B)

b = B()
print(super(B, b).who(), "|", super(B, b))   # forma explícita: super(Classe, instância)


# O super() olha o MRO da INSTÂNCIA, a partir de depois de `__class__`
class C(A):
    def who(self):
        return "C>" + super().who()


class D(B, C):
    pass


print([cls.__name__ for cls in D.__mro__])
print(D().who())
# O super() dentro de B, para uma instância de D, vai para C (e não para A)

try:
    super().who()                              # fora de uma classe
except RuntimeError as error:
    print("RuntimeError:", error)
