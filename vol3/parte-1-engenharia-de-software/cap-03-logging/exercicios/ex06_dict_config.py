"""Exercício 6: montar uma configuração para dictConfig."""


def build_config(app, level="INFO", log_file=None):
    """Devolve um dict para ``logging.config.dictConfig``:

    * ``version`` 1 e ``disable_existing_loggers`` ``False``;
    * formatter ``"plain"`` com ``"%(asctime)s %(levelname)s %(name)s: %(message)s"``;
    * handler ``"console"``: ``logging.StreamHandler`` com o formatter, para
      ``"ext://sys.stderr"``;
    * se ``log_file`` não for ``None``: handler ``"file"``:
      ``logging.handlers.RotatingFileHandler`` (``filename=str(log_file)``,
      ``maxBytes=1_000_000``, ``backupCount=3``, ``encoding="utf-8"``) com o
      mesmo formatter;
    * logger ``app`` com ``level`` (texto em maiúsculas), todos os handlers
      acima e ``propagate`` ``False``;
    * ``root`` com nível ``"WARNING"`` e o handler ``"console"``.
    """
    raise NotImplementedError
