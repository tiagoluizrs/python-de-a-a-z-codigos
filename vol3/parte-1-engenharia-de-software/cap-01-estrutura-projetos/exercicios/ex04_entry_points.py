"""Exercício 4: resolver pontos de entrada ("pacote.modulo:funcao")."""


def parse_entry_point(spec):
    """``"pkg.mod:func"`` -> ``("pkg.mod", "func")``; também aceita um atributo
    com pontos (``"pkg.mod:Class.method"`` -> ``("pkg.mod", "Class.method")``).
    Formato inválido (sem ``:``, ou parte vazia, ou espaços) levanta
    ``ValueError``."""
    raise NotImplementedError


def load_entry_point(spec):
    """Importa o módulo (``importlib.import_module``) e devolve o objeto
    apontado, percorrendo atributos com pontos. Módulo inexistente levanta
    ``ImportError``; atributo inexistente levanta ``AttributeError``."""
    raise NotImplementedError


def run_entry_point(spec, argv):
    """Carrega o ponto de entrada e chama com ``argv`` (lista); converte o
    retorno em código de saída: ``None`` vira ``0``, ``int`` é mantido, ``str``
    vira ``1``. Devolve o código (não chama ``sys.exit``)."""
    raise NotImplementedError
