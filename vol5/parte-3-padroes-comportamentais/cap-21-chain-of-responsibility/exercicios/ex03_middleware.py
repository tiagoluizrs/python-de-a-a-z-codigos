"""Exercício 3: o MIDDLEWARE: cada elo recebe o pedido e o PRÓXIMO elo, e decide se chama, o que faz antes e depois, e se curto-circuita."""


def compose(*middlewares):
    """``compose(a, b, c)(handler)`` devolve uma função ``app(request)`` equivalente a ``a(request, lambda r: b(r, lambda r: c(r, handler)))``: o PRIMEIRO middleware é o mais EXTERNO
    (executa primeiro na ida e por último na volta). Um middleware é ``mw(request, call_next) -> response``. Sem middlewares, devolve o próprio ``handler``. Um elemento que não é chamável:
    ``TypeError("middleware precisa ser chamável")`` (na composição, ao aplicar ao handler)."""
    raise NotImplementedError


def logging_mw(log: list):
    """Acrescenta ``f"-> {request['path']}"`` a ``log`` antes de chamar o próximo e ``f"<- {response['status']}"`` DEPOIS (com a resposta do próximo); se o próximo levantar exceção,
    acrescenta ``f"!! {tipo_da_exceção}"`` e relança."""
    raise NotImplementedError


def auth_mw(valid_tokens: set):
    """Se ``request.get("token")`` não está em ``valid_tokens``, CURTO-CIRCUITA: devolve ``{"status": 401, "body": "não autorizado"}`` sem chamar o próximo. Senão, repassa."""
    raise NotImplementedError


def rate_limit_mw(limit: int, window: float, clock):
    """Limita o número de pedidos por ``request["client"]`` (padrão ``"anon"``) a ``limit`` em cada janela de ``window`` segundos (janela deslizante: guarde os instantes
    ``clock()`` dos pedidos aceitos de cada cliente e descarte os com ``agora - instante >= window``). Excedido: ``{"status": 429, "body": "muitos pedidos"}`` SEM chamar o próximo e SEM
    contar o pedido recusado. ``limit < 1`` ou ``window <= 0``: ``ValueError`` na criação."""
    raise NotImplementedError


def cache_mw(methods=("GET",)):
    """Guarda a resposta dos pedidos cujo ``request.get("method", "GET")`` está em ``methods`` e cuja resposta tem ``status == 200``, por ``request["path"]``; um pedido repetido devolve a
    resposta guardada SEM chamar o próximo (e a resposta guardada vem com ``"cached": True`` acrescentado, em uma CÓPIA: a original não muda). Respostas que não são 200 não são guardadas.
    Pedidos de outros métodos passam direto e INVALIDAM (apagam) a entrada daquele ``path``."""
    raise NotImplementedError
