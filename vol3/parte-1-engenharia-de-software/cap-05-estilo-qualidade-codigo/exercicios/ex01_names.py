"""Exercício 1: verificador de nomes (PEP 8)."""


def check_names(source):
    """Devolve a lista ORDENADA de achados ``(linha, código, nome)`` do texto
    de código ``source`` (use ``ast``):

    * ``"N801"``: nome de CLASSE fora de CapWords (começa com maiúscula, sem
      ``_``; um ``_`` inicial é permitido: ``_Helper``);
    * ``"N802"``: nome de FUNÇÃO ou MÉTODO que não é minúsculo com ``_``
      (``getUser`` e ``Process`` são achados; ``__init__`` e ``_privado`` não);
    * ``"N803"``: nome de ARGUMENTO com letra maiúscula (``self`` e ``cls``
      estão sempre ok);
    * ``"N806"``: variável local atribuída em função com letra maiúscula.

    Considere ``def``, ``async def``, ``lambda`` ignorado. Ordene por
    ``(linha, código, nome)``."""
    raise NotImplementedError
