"""Exercício 3: idempotência: executar duas vezes (a entrega é "pelo menos uma vez") sem repetir o efeito."""


class IdempotentExecutor:
    """Garante que o efeito de ``fn`` para uma mesma ``key`` aconteça UMA vez.

    * ``IdempotentExecutor(clock, ttl=None)``: ``clock()`` dá o agora (segundos); ``ttl`` é por quanto tempo um resultado fica
      lembrado (``None`` = para sempre);
    * ``run(key, fn)``: se ``key`` já foi concluída (e não expirou), devolve o resultado GUARDADO sem chamar ``fn``;
      senão chama ``fn()``, guarda o resultado e o devolve;
    * se ``fn`` levantar exceção, a ``key`` NÃO fica marcada como concluída (a próxima tentativa executa de novo) e a exceção sobe;
    * chamadas CONCORRENTES com a mesma ``key`` (threads): ``fn`` roda uma única vez; as outras esperam e recebem o mesmo
      resultado (se ``fn`` falhar, a primeira recebe a exceção e a seguinte tenta de novo, executando ``fn``);
    * ``key`` diferentes não se bloqueiam entre si;
    * ``stats``: um dict com ``executed`` (quantas vezes ``fn`` rodou com sucesso), ``replayed`` (quantas respostas vieram do
      guardado) e ``failed`` (quantas ``fn`` falharam)."""

    def __init__(self, clock, ttl: float | None = None):
        raise NotImplementedError

    def run(self, key: str, fn):
        raise NotImplementedError

    @property
    def stats(self) -> dict:
        raise NotImplementedError


def make_key(task_name: str, **params) -> str:
    """A chave de idempotência de uma tarefa: ``"nome|a=1|b=2"`` com os parâmetros em ordem alfabética do nome, valores com
    ``str()``. Parâmetros com valor ``None`` são ignorados (``make_key("pay", order=7, coupon=None)`` -> ``"pay|order=7"``)."""
    raise NotImplementedError
