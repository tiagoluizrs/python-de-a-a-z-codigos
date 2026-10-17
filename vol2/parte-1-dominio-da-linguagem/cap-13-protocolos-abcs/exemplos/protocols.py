"""typing.Protocol: tipagem estrutural (para o verificador e, se pedido, em runtime)."""
import io
from typing import Protocol, SupportsFloat, SupportsIndex, runtime_checkable


class SupportsClose(Protocol):
    def close(self) -> None: ...


@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...


@runtime_checkable
class HasName(Protocol):
    name: str                                   # atributo de dados


def shutdown(resource: SupportsClose) -> None:   # o verificador checa a forma
    resource.close()


class Connection:                                # não herda de nada
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


conn = Connection()
shutdown(conn)
print("fechou:", conn.closed)

# Sem @runtime_checkable, isinstance é recusado
try:
    isinstance(conn, SupportsClose)
except TypeError as error:
    print("TypeError:", error)

# Com @runtime_checkable: só verifica a PRESENÇA do método
print(isinstance(conn, Closeable), isinstance(io.StringIO(), Closeable), isinstance(42, Closeable))


class WrongSignature:
    def close(self, a, b, c):                    # assinatura incompatível
        return "não confere com o protocolo"


print("assinatura errada passa no isinstance?", isinstance(WrongSignature(), Closeable))

# Protocolos com atributos: isinstance funciona, issubclass não
class Person:
    def __init__(self, name):
        self.name = name


print(isinstance(Person("Ana"), HasName), isinstance(object(), HasName))
try:
    issubclass(Person, HasName)
except TypeError as error:
    print("TypeError:", error)

# Protocolos prontos em typing
class Meters:
    def __float__(self):
        return 1.5

    def __index__(self):
        return 2


print(isinstance(Meters(), SupportsFloat), isinstance(Meters(), SupportsIndex), isinstance("a", SupportsFloat))
import typing
print(sorted(typing.get_protocol_members(Closeable)), typing.is_protocol(Closeable), typing.is_protocol(Connection))
