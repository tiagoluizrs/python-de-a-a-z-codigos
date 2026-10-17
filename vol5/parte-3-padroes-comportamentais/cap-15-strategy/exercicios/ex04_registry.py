"""Exercício 4: escolher a estratégia: por nome (registro) e por REGRAS sobre o contexto."""


class StrategyRegistry:
    """Guarda estratégias (callables) por nome e escolhe uma para cada contexto.

    * ``register(name, *, default=False)``: DECORADOR que guarda a função sob ``name`` e a devolve inalterada; ``default=True`` a marca como padrão. Nome já usado:
      ``ValueError(f"estratégia já registrada: {name}")``; um segundo padrão: ``ValueError("já existe um padrão: {nome}")`` (com o nome do atual);
    * ``get(name=None)``: a estratégia pelo nome; ``None`` pede a padrão (sem padrão: ``LookupError("sem estratégia padrão")``); nome desconhecido:
      ``KeyError(f"estratégia desconhecida: {name}; disponíveis: a, b")`` (alfabético; ``disponíveis: nenhuma`` se vazio);
    * ``names()``: os nomes em ordem alfabética;
    * ``add_rule(predicate, name)``: acrescenta uma regra (``predicate(context) -> bool``); ``name`` precisa existir (``KeyError`` como em ``get``); as regras valem na
      ordem em que foram acrescentadas;
    * ``resolve(context)``: a estratégia da PRIMEIRA regra cujo predicado é verdadeiro; se nenhuma, a padrão (ou ``LookupError("sem estratégia padrão")``);
    * ``run(context, *args, **kwargs)``: ``resolve(context)(*args, **kwargs)``."""

    def __init__(self):
        raise NotImplementedError

    def register(self, name: str, *, default: bool = False):
        raise NotImplementedError

    def get(self, name: str | None = None):
        raise NotImplementedError

    def names(self) -> list[str]:
        raise NotImplementedError

    def add_rule(self, predicate, name: str) -> None:
        raise NotImplementedError

    def resolve(self, context):
        raise NotImplementedError

    def run(self, context, *args, **kwargs):
        raise NotImplementedError
