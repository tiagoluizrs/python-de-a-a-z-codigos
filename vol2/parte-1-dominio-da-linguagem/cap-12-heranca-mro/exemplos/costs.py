"""Custo de chamar métodos herdados e de usar super()."""
import timeit


class Base:
    def method(self):
        return 1


class Level1(Base):
    pass


class Level2(Level1):
    pass


class Level3(Level2):
    pass


class Level4(Level3):
    pass


class Override(Base):
    def method(self):
        return 2


class WithSuper(Base):
    def method(self):
        return super().method() + 1


class WithExplicit(Base):
    def method(self):
        return Base.method(self) + 1


objects = {name: cls() for name, cls in [
    ("base", Base), ("level4", Level4), ("override", Override),
    ("with_super", WithSuper), ("with_explicit", WithExplicit)]}
for label, key in [("método na própria classe", "base"),
                   ("herdado de 4 níveis acima", "level4"),
                   ("sobrescrito", "override"),
                   ("sobrescrito + super().method()", "with_super"),
                   ("sobrescrito + Base.method(self)", "with_explicit")]:
    seconds = min(timeit.repeat("obj.method()", globals={"obj": objects[key]},
                                number=1_000_000, repeat=5)) / 1_000_000
    print(f"{label:<34}{seconds * 1e9:7.1f} ns")
