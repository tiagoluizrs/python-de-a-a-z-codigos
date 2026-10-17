"""Gabarito do exercício 1."""
import logging

FORMAT = "%(levelname)s %(name)s: %(message)s"


def _resolve_level(level):
    if isinstance(level, int):
        return level
    mapping = logging.getLevelNamesMapping()
    try:
        return mapping[level.upper()]
    except (KeyError, AttributeError):
        raise ValueError(f"nível desconhecido: {level!r}") from None


def configure_logging(name, level="INFO", stream=None):
    numeric = _resolve_level(level)
    logger = logging.getLogger(name)
    for handler in list(logger.handlers):
        if getattr(handler, "_configure_logging", False):
            logger.removeHandler(handler)
    handler = logging.StreamHandler(stream)
    handler._configure_logging = True
    handler.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(handler)
    logger.setLevel(numeric)
    logger.propagate = False
    return logger
