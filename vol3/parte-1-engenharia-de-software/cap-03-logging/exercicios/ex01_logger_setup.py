"""Exercício 1: configurar um logger de aplicação, sem duplicar handlers."""
import logging


def configure_logging(name, level="INFO", stream=None):
    """Configura e devolve o logger ``name``:

    * nível a partir de ``level`` (texto como ``"debug"`` em qualquer caixa,
      ou número); nome desconhecido levanta ``ValueError``
      (``logging.getLevelNamesMapping()`` ajuda);
    * UM ``StreamHandler(stream)`` com o formato
      ``"%(levelname)s %(name)s: %(message)s"`` (``stream=None`` usa
      ``sys.stderr``);
    * ``propagate = False``;
    * chamar de novo com o mesmo ``name`` NÃO acumula handlers: o handler
      antigo (criado por esta função) é substituído, para respeitar o novo
      ``stream``/``level``.
    """
    raise NotImplementedError
