"""O Python valida o que os métodos especiais devolvem."""


def show(label, func):
    try:
        result = func()
        print(f"{label:<22}= {result!r}")
    except Exception as error:
        print(f"{label:<22}{type(error).__name__}: {error}")


class NegativeLen:
    def __len__(self):
        return -1


class StrLen:
    def __len__(self):
        return "3"


class IntBool:
    def __bool__(self):
        return 1


class BadRepr:
    def __repr__(self):
        return 42


class BadIter:
    def __iter__(self):
        return 5


class BadHash:
    def __hash__(self):
        return "x"


class FloatIndex:
    def __index__(self):
        return 1.5


show("len(__len__ = -1)", lambda: len(NegativeLen()))
show("len(__len__ = '3')", lambda: len(StrLen()))
show("bool(__bool__ = 1)", lambda: bool(IntBool()))
show("repr(__repr__ = 42)", lambda: repr(BadRepr()))
show("iter(__iter__ = 5)", lambda: iter(BadIter()))
show("hash(__hash__ = 'x')", lambda: hash(BadHash()))
show("[1,2][__index__=1.5]", lambda: [1, 2][FloatIndex()])
number, text = 5, "a"
show("len(5)", lambda: len(number))
show("5[0]", lambda: number[0])
show("for x in 5", lambda: [x for x in number])
show("5()", lambda: number())
show("-'a'", lambda: -text)
