"""Exercício 4: a dependência "ambiente" com ``contextvars``: o contexto de uma requisição, sem passar parâmetros por dez funções (e os limites dessa ideia)."""
import contextvars
from contextlib import contextmanager

_request_id = contextvars.ContextVar("request_id")              # (Pronto.) as variáveis de contexto
_user = contextvars.ContextVar("user")


@contextmanager
def request_scope(request_id: str, user: str | None = None):
    """Abre uma "requisição": dentro do ``with``, ``current_request_id()`` devolve ``request_id`` e ``current_user()`` devolve ``user``.

    * ``request_id`` vazio (ou só espaços): ``ValueError("request_id inválido")``;
    * usa ``ContextVar.set`` e SEMPRE restaura os valores anteriores ao sair (``reset`` com o *token*), mesmo se o bloco levantar uma exceção; escopos ANINHADOS restauram o de fora;
    * ``user`` ``None`` quer dizer "anônimo"."""
    raise NotImplementedError
    yield


def current_request_id() -> str:
    """O id da requisição atual; fora de qualquer ``request_scope``: ``LookupError("fora de uma requisição")``."""
    raise NotImplementedError


def current_user() -> str | None:
    """O usuário da requisição atual (``None`` se anônimo); fora de qualquer escopo: ``LookupError("fora de uma requisição")``."""
    raise NotImplementedError


def in_request() -> bool:
    """``True`` se há uma requisição ativa neste contexto."""
    raise NotImplementedError


def log_prefix() -> str:
    """O prefixo dos registros: ``"[req-1 ana] "`` (id e usuário) ou ``"[req-1 anônimo] "``; fora de uma requisição: ``"[-] "`` (SEM levantar erro)."""
    raise NotImplementedError


def run_in_thread(fn, *args):
    """Executa ``fn(*args)`` em uma NOVA ``threading.Thread`` e devolve o resultado (ou propaga a exceção que a função levantou). A thread nova enxerga o MESMO contexto de quem chamou
    (uma thread NÃO herda as variáveis de contexto sozinha: copie o contexto atual com ``contextvars.copy_context()`` e execute ``fn`` dentro dele com ``ctx.run``)."""
    raise NotImplementedError
