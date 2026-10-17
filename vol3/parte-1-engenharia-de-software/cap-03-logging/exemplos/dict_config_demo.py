"""dictConfig: a configuração declarativa, e três armadilhas."""
import io
import logging
import logging.config

# 1) disable_existing_loggers: o padrão (True) silencia loggers criados ANTES da configuração
pre_existing = logging.getLogger("pre.existing")
logging.config.dictConfig({"version": 1, "handlers": {"c": {"class": "logging.StreamHandler"}},
                           "root": {"level": "INFO", "handlers": ["c"]}})
print("com o padrão, pre.existing.disabled =", pre_existing.disabled)
logging.config.dictConfig({"version": 1, "disable_existing_loggers": False, "root": {"level": "INFO", "handlers": []}})
pre_existing.disabled = False

# 2) Uma configuração completa
CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(levelname)s:%(name)s:%(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain", "stream": "ext://sys.stdout"}},
    "loggers": {"myapp": {"level": "DEBUG", "handlers": ["console"], "propagate": False}},
    "root": {"level": "WARNING", "handlers": ["console"]},
}
logging.config.dictConfig(CONFIG)
logging.getLogger("myapp.db").debug("detalhe do myapp")                 # nível DEBUG só para myapp
logging.getLogger("terceiro").info("ruído de terceiro (WARNING na raiz)")
logging.getLogger("terceiro").warning("aviso de terceiro")

# 3) QueueHandler configurado: o listener NÃO é iniciado sozinho
queue_config = {
    "version": 1, "disable_existing_loggers": False,
    "handlers": {"out": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout"},
                 "queue": {"class": "logging.handlers.QueueHandler", "handlers": ["out"], "respect_handler_level": True}},
    "root": {"level": "INFO", "handlers": ["queue"]},
}
logging.config.dictConfig(queue_config)
handler = logging.getLogger().handlers[0]
logging.getLogger("q").info("antes de start()")
print("thread do listener:", handler.listener._thread, "| na fila:", handler.queue.qsize())
handler.listener.start()
logging.getLogger("q").info("depois de start()")
handler.listener.stop()                                                  # esvazia a fila e para
print("na fila agora:", handler.queue.qsize())
