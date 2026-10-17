"""Exercício 1: um decorador de classe de registro."""

HANDLERS: dict[str, type] = {}


def handler(name):
    """Decorador de classe com parâmetro: ``@handler("csv")``.

    * registra a classe em ``HANDLERS[name]``;
    * devolve a MESMA classe;
    * se ``name`` já estiver registrado, levanta ``ValueError``;
    * acrescenta o atributo ``handler_name`` (= ``name``) na classe.
    """
    raise NotImplementedError
