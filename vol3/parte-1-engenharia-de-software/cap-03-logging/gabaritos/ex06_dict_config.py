"""Gabarito do exercício 6."""


def build_config(app, level="INFO", log_file=None):
    handlers = {"console": {"class": "logging.StreamHandler", "formatter": "plain", "stream": "ext://sys.stderr"}}
    if log_file is not None:
        handlers["file"] = {"class": "logging.handlers.RotatingFileHandler", "formatter": "plain",
                            "filename": str(log_file), "maxBytes": 1_000_000, "backupCount": 3, "encoding": "utf-8"}
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"plain": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}},
        "handlers": handlers,
        "loggers": {app: {"level": level.upper(), "handlers": list(handlers), "propagate": False}},
        "root": {"level": "WARNING", "handlers": ["console"]},
    }
