"""Exercício 4: registro de plugins e depreciação."""

PLUGINS = {}


def register(name):
    """Fábrica de decoradores que registra a função em ``PLUGINS``.

    - ``@register("csv")`` guarda a função em ``PLUGINS["csv"]``;
    - a função original é devolvida SEM embrulho (mesmo objeto);
    - registrar um nome já existente levanta ``ValueError``.
    """
    raise NotImplementedError


def run(name, *args, **kwargs):
    """Chama o plugin ``name``; levanta ``KeyError`` com mensagem
    ``unknown plugin: <name>`` se não existir."""
    raise NotImplementedError


def deprecated(reason):
    """Fábrica de decoradores que avisa o uso de função obsoleta.

    - emita ``DeprecationWarning`` com a mensagem
      ``"<nome> is deprecated: <reason>"`` a cada chamada;
    - use ``stacklevel=2`` para que o aviso aponte para o CHAMADOR;
    - preserve os metadados com ``functools.wraps``.
    """
    raise NotImplementedError
