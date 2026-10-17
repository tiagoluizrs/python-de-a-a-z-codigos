"""Gabarito do exercício 2."""


class NullLogger:
    def info(self, message, *args, **kwargs):
        return None

    warning = error = info


class NullCache:
    def get(self, key, default=None):
        return default

    def set(self, key, value):
        return None

    def __contains__(self, key):
        return False

    def __len__(self):
        return 0


class NullNotifier:
    def send(self, to, message):
        return False


NULL_LOGGER = NullLogger()
NULL_CACHE = NullCache()
NULL_NOTIFIER = NullNotifier()


class ReportService:
    def __init__(self, compute, logger=None, cache=None, notifier=None):
        self.compute = compute
        self.logger = NULL_LOGGER if logger is None else logger
        self.cache = NULL_CACHE if cache is None else cache
        self.notifier = NULL_NOTIFIER if notifier is None else notifier

    def report(self, key):
        cached = self.cache.get(key)
        if cached is not None:
            self.logger.info(f"cache hit: {key}")
            return cached
        try:
            value = self.compute(key)
        except Exception as error:
            self.logger.error(f"falhou: {key}: {type(error).__name__}")
            raise
        self.logger.info(f"calculado: {key}")
        self.cache.set(key, value)
        return value

    def report_and_notify(self, key, to):
        value = self.report(key)
        sent = self.notifier.send(to, f"relatório {key}: {value}")
        if not sent:
            self.logger.error(f"não enviado para {to}")
        return value, sent
