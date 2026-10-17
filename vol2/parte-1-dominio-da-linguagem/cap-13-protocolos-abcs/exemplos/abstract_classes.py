"""abc.ABC e @abstractmethod: contratos que o Python exige."""
from abc import ABC, abstractmethod


class Exporter(ABC):
    """Interface + método-gabarito concreto."""

    @property
    @abstractmethod
    def extension(self):
        """Extensão do arquivo (sem ponto)."""

    @abstractmethod
    def render(self, rows):
        """Converte linhas em texto."""

    def filename(self, stem):                    # método CONCRETO, herdado
        return f"{stem}.{self.extension}"

    def export(self, stem, rows):                # Template Method
        return self.filename(stem), self.render(rows)


try:
    Exporter()
except TypeError as error:
    print("TypeError:", error)


class Half(Exporter):
    extension = "txt"                            # implementou só uma


try:
    Half()
except TypeError as error:
    print("TypeError:", error)


class CsvExporter(Exporter):
    extension = "csv"

    def render(self, rows):
        return "\n".join(",".join(map(str, row)) for row in rows)


csv = CsvExporter()
print(csv.export("dados", [(1, "a"), (2, "b")]))
print(Exporter.__abstractmethods__, CsvExporter.__abstractmethods__)
print(isinstance(csv, Exporter), issubclass(CsvExporter, Exporter))


# Um método abstrato PODE ter implementação, chamada via super()
class Base(ABC):
    @abstractmethod
    def greet(self):
        return "olá da base"


class Impl(Base):
    def greet(self):
        return super().greet() + " e da subclasse"


print(Impl().greet())


# Registro virtual: a classe de terceiros vira "subclasse" sem herdar
class Drawable(ABC):
    @abstractmethod
    def draw(self): ...


class ThirdParty:                                # você não controla esta classe
    def draw(self):
        return "desenhado"


print("antes :", issubclass(ThirdParty, Drawable))
Drawable.register(ThirdParty)
print("depois:", issubclass(ThirdParty, Drawable), isinstance(ThirdParty(), Drawable))
print("MRO não muda:", [c.__name__ for c in ThirdParty.__mro__])


# __subclasshook__: o "isinstance estrutural" das ABCs de um método
class Closeable(ABC):
    @abstractmethod
    def close(self): ...

    @classmethod
    def __subclasshook__(cls, candidate):
        if cls is Closeable:
            if any("close" in klass.__dict__ for klass in candidate.__mro__):
                return True
        return NotImplemented


import io
print("StringIO é Closeable?", isinstance(io.StringIO(), Closeable), "| int?", isinstance(1, Closeable))
