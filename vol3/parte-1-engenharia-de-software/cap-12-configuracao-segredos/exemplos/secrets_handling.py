"""Segredos: não vazar em repr, logs, tracebacks e processos filhos."""
import hmac
import io
import json
import logging
from dataclasses import dataclass, field


class Secret:
    """Um valor sensível que nunca aparece sozinho em texto."""

    __slots__ = ("_value",)

    def __init__(self, value):
        object.__setattr__(self, "_value", value)

    def reveal(self):
        return self._value

    def __repr__(self):
        return "Secret('**********')"

    __str__ = __repr__

    def __eq__(self, other):
        return isinstance(other, Secret) and hmac.compare_digest(self._value.encode(), other._value.encode())

    __hash__ = None

    def __reduce__(self):
        raise TypeError("Secret não pode ser serializado")


@dataclass
class Settings:
    user: str
    password: Secret
    token: str = field(repr=False, default="tok-123")        # alternativa simples: fora do repr


settings = Settings("ana", Secret("s3nh4-super-secreta"))
print("repr da configuração:", settings)
print("f-string:", f"senha={settings.password}", "| reveal só onde precisa:", settings.password.reveal()[:3] + "...")

# O erro clássico: logar o objeto de configuração inteiro (sem proteção)
@dataclass
class Unsafe:
    user: str
    password: str


buffer = io.StringIO()
log = logging.getLogger("secrets.demo")
log.addHandler(logging.StreamHandler(buffer))
log.setLevel(logging.INFO)
log.propagate = False
log.info("config carregada: %s", Unsafe("ana", "s3nh4-super-secreta"))
log.info("config carregada: %s", settings)
for line in buffer.getvalue().splitlines():
    print("  log:", line)

# Traceback: valores locais não aparecem por padrão, mas o repr em mensagens sim
try:
    raise ValueError(f"falha de login com {settings.password!r}")
except ValueError as error:
    print("mensagem de erro com o objeto protegido:", error)

# JSON e pickle
try:
    json.dumps({"p": settings.password})
except TypeError as error:
    print("json.dumps:", error)
print("json com default seguro:", json.dumps({"p": settings.password}, default=lambda o: "***"))
import pickle

try:
    pickle.dumps(settings.password)
except TypeError as error:
    print("pickle:", error)

# Comparação: tempo constante
print("iguais:", Secret("abc") == Secret("abc"), "| diferentes:", Secret("abc") == Secret("abd"))
