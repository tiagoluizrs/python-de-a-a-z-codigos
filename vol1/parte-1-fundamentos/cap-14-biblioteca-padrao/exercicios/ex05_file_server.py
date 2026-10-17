"""Exercício 5: servidor de arquivos local, em thread, para testes."""
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def serve_directory(directory: Path) -> Iterator[str]:
    """Sirva ``directory`` por HTTP em 127.0.0.1 e devolva (yield) a URL
    base, por exemplo ``"http://127.0.0.1:54321"``.

    Requisitos:
    - porta 0 (o sistema escolhe uma livre), só em ``127.0.0.1``;
    - ``ThreadingHTTPServer`` + ``SimpleHTTPRequestHandler`` com
      ``functools.partial(..., directory=str(directory))``;
    - ``serve_forever`` numa ``threading.Thread`` daemon;
    - ao sair do ``with``: ``shutdown()``, ``server_close()`` e ``join()``,
      mesmo se houver exceção (use ``try/finally``).
    - silencie o log de acessos sobrescrevendo ``log_message``.
    """
    raise NotImplementedError
    yield ""  # noqa: o yield faz desta função um gerador
