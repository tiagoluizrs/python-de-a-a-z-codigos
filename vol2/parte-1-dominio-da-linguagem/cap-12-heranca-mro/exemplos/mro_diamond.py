"""O problema do diamante e o MRO (C3)."""


class A:
    def hello(self):
        return ["A"]


class B(A):
    def hello(self):
        return ["B"] + super().hello()


class C(A):
    def hello(self):
        return ["C"] + super().hello()


class D(B, C):
    def hello(self):
        return ["D"] + super().hello()


print([cls.__name__ for cls in D.__mro__])
print(D().hello())                      # A aparece UMA vez, depois de B e C
print([cls.__name__ for cls in B.__mro__], [cls.__name__ for cls in C.__mro__])


# A ordem das bases importa
class E(C, B):
    pass


print([cls.__name__ for cls in E.__mro__])
print(E().hello())


# Uma ordem impossível é recusada na criação da classe
class X:
    pass


class Y(X):
    pass


try:
    class Z(X, Y):                      # X antes de Y, mas Y é filha de X
        pass
except TypeError as error:
    print("TypeError:", error)


# Um exemplo maior (a figura clássica das listas de linearização)
class O:
    pass


class A1(O): pass
class B1(O): pass
class C1(O): pass
class D1(O): pass
class E1(O): pass
class K1(A1, B1, C1): pass
class K2(D1, B1, E1): pass
class K3(D1, A1): pass
class Z1(K1, K2, K3): pass


print([cls.__name__ for cls in Z1.__mro__])
