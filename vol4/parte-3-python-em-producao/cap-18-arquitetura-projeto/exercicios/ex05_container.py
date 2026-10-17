"""Exercício 5: uma RAIZ DE COMPOSIÇÃO mínima: um contêiner de dependências com singletons, sobrescritas para teste e ciclos."""


class DependencyError(Exception):
    pass


class Container:
    """Registra FÁBRICAS pelo nome e entrega as instâncias sob demanda.

    * ``register(name, factory, singleton=True)``: ``factory`` é um callable que recebe o PRÓPRIO contêiner
      (``factory(container)``) e devolve o objeto (assim ele pede as suas dependências com ``container.get(...)``); nome
      repetido: ``DependencyError``;
    * ``get(name)``: nome desconhecido: ``DependencyError(f"desconhecido: {name}")``; com ``singleton=True`` a fábrica roda UMA
      vez e a instância é reaproveitada; com ``singleton=False``, uma nova a cada ``get``;
    * ciclo (``a`` precisa de ``b`` que precisa de ``a``): ``DependencyError("ciclo: a -> b -> a")`` (o caminho, começando pelo nome
      pedido primeiro) em vez de estourar a recursão; depois do erro, o contêiner continua utilizável;
    * ``override(name, value)``: gerenciador de contexto que, dentro do ``with``, faz ``get(name)`` devolver ``value`` (um
      objeto pronto, p. ex. um dublê de teste) e, ao sair, restaura o comportamento anterior (inclusive um singleton já
      criado); ``name`` precisa existir (senão ``DependencyError``); funciona mesmo com ``override`` aninhado;
    * ``built``: o conjunto dos nomes cujas fábricas já rodaram (para provar que a criação é PREGUIÇOSA)."""

    def __init__(self):
        raise NotImplementedError

    def register(self, name: str, factory, singleton: bool = True) -> None:
        raise NotImplementedError

    def get(self, name: str):
        raise NotImplementedError

    def override(self, name: str, value):
        raise NotImplementedError

    @property
    def built(self) -> set[str]:
        raise NotImplementedError
