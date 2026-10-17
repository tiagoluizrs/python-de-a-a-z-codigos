"""Exercício 2: a cadeia como LISTA de funções (cada uma devolve um resultado ou ``None`` para repassar)."""


def first_match(handlers, request, default=None):
    """Chama os ``handlers`` em ordem com ``request`` e devolve o PRIMEIRO resultado que NÃO seja ``None`` (``0``, ``""`` e ``False`` contam como resultado!). Os seguintes NÃO são
    chamados depois que um resolve. Nenhum resolveu: ``default``. ``handlers`` pode ser qualquer iterável (inclusive um gerador, consumido só até o necessário)."""
    raise NotImplementedError


class Router:
    """Uma cadeia declarativa: ``register(predicate, handler)`` acrescenta um par ao FIM da lista (devolve ``handler``, para servir como decorador: ``@router.register(pred)`` não
    é necessário aqui; use a forma de chamada); ``route(request)`` chama o ``handler`` do PRIMEIRO par cujo ``predicate(request)`` é verdadeiro e devolve o resultado dele (que pode
    ser ``None``); nenhum casou: ``LookupError("nenhuma rota para ...")`` com o ``repr`` da requisição. ``fallback`` (opcional no construtor, ``Router(fallback=None)``): se dado,
    é chamado quando nenhuma rota casa, em vez do ``LookupError``.

    * ``insert(index, predicate, handler)``: coloca o par na posição dada (para dar PRIORIDADE a uma regra);
    * ``remove(handler)``: tira os pares desse ``handler`` e devolve quantos tirou;
    * ``len(router)`` e ``handlers()`` (lista, em ordem, dos handlers)."""

    def __init__(self, fallback=None):
        raise NotImplementedError

    def register(self, predicate, handler):
        raise NotImplementedError

    def insert(self, index: int, predicate, handler) -> None:
        raise NotImplementedError

    def remove(self, handler) -> int:
        raise NotImplementedError

    def route(self, request):
        raise NotImplementedError

    def handlers(self) -> list:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


def classify(text: str) -> str:
    """Classifica uma mensagem com UMA cadeia de regras (use ``first_match`` com funções, sem ``if/elif``): em ordem, ``"spam"`` se contém ``"compre agora"`` (sem diferenciar maiúsculas
    de minúsculas); ``"urgente"`` se contém ``"urgente"`` OU termina com ``"!!!"``; ``"pergunta"`` se termina com ``"?"``; ``"vazia"`` se, sem espaços nas pontas, é vazia
    (verificada PRIMEIRO, antes de todas as outras); senão ``"comum"`` (o ``default``)."""
    raise NotImplementedError
