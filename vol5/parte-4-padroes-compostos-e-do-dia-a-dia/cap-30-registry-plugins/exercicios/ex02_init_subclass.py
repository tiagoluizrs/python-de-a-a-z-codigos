"""Exercício 2: o registro AUTOMÁTICO por ``__init_subclass__``: declarar a classe já a registra, sem nenhuma linha de registro."""


class Exporter:
    """A base dos exportadores. O dicionário ``Exporter.registry`` (atributo de classe, compartilhado) guarda nome -> classe.

    Ao criar uma subclasse (``class CsvExporter(Exporter): ...``), o ``__init_subclass__(cls, name=None, abstract=False, **kwargs)`` a registra:

    * o nome é ``name`` (se dado) ou o nome da classe SEM o sufixo ``"Exporter"`` (``removesuffix``), em MINÚSCULAS; nome vazio (a classe se chama só ``Exporter``-alguma-coisa que
      sobra ``""``): ``ValueError("nome vazio")``; nome já usado: ``ValueError(f"exportador já registrado: {nome}")``;
    * ``abstract=True`` NÃO registra a classe (uma intermediária); essa opção NÃO é herdada (as subclasses dela são registradas, a não ser que digam ``abstract=True`` também);
    * as subclasses de uma classe concreta já registrada também se registram (herança em vários níveis);
    * os OUTROS argumentos (``kwargs``) são repassados a ``super().__init_subclass__(**kwargs)``, que recusa o que não conhece com ``TypeError``: e, se isso acontecer, a classe NÃO fica
      registrada (chame o ``super`` ANTES de registrar);
    * ``extension`` (atributo de classe, ``""`` por padrão) é a extensão do arquivo gerado, ex.: ``".csv"``.

    Métodos de classe:

    * ``create(name, *args, **kwargs)``: instancia a classe registrada; nome desconhecido (a busca ignora maiúsculas e espaços nas pontas):
      ``KeyError(f"exportador desconhecido: {name!r}; disponíveis: a, b")`` (nomes em ordem; ``nenhum`` se vazio);
    * ``names()``: os nomes em ordem alfabética; ``unregister(name)``: remove e devolve a classe (``KeyError`` como no ``create`` se não existe);
    * ``for_extension(ext)``: a classe registrada cuja ``extension`` é ``ext`` (sem diferenciar maiúsculas; se há várias, a de MENOR nome); nenhuma: ``KeyError(f"nenhum exportador para {ext!r}")``.

    O método de instância ``export(rows)`` da base levanta ``NotImplementedError``."""

    registry: dict = {}
    extension: str = ""

    def __init_subclass__(cls, name=None, abstract=False, **kwargs):
        raise NotImplementedError

    @classmethod
    def create(cls, name: str, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def names(cls) -> list[str]:
        raise NotImplementedError

    @classmethod
    def unregister(cls, name: str):
        raise NotImplementedError

    @classmethod
    def for_extension(cls, ext: str):
        raise NotImplementedError

    def export(self, rows):
        raise NotImplementedError
