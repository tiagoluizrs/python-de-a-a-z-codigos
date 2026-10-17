"""Exercício 2: colaboradores opcionais (logger, cache, notificador) que viram Null Objects: o serviço NUNCA pergunta ``if self.logger``."""


class NullLogger:
    """``info``, ``warning`` e ``error`` aceitam ``(message, *args, **kwargs)`` e não fazem nada (devolvem ``None``)."""


class NullCache:
    """Um cache que nunca guarda: ``get(key, default=None)`` devolve SEMPRE ``default``; ``set(key, value)`` não faz nada; ``key in cache`` é ``False``; ``len(cache)`` é ``0``."""


class NullNotifier:
    """``send(to, message)`` não envia nada e devolve ``False`` (``True`` seria "enviado")."""


NULL_LOGGER = NullLogger()
NULL_CACHE = NullCache()
NULL_NOTIFIER = NullNotifier()


class ReportService:
    """``ReportService(compute, logger=None, cache=None, notifier=None)``.

    * um colaborador que é ``None`` (e SÓ nesse caso: compare com ``is None``, NUNCA use ``or``, porque um cache vazio é FALSO por causa do ``__len__``) é trocado por ``NULL_LOGGER``,
      ``NULL_CACHE`` ou ``NULL_NOTIFIER``; os atributos ``logger``, ``cache`` e ``notifier`` guardam o que será usado;
    * o ``logger`` tem ``info(msg)`` e ``error(msg)``; o ``cache``, ``get(key)`` (``None`` é "não achei") e ``set(key, value)``; o ``notifier``, ``send(to, message)`` (``True`` se enviou);
    * ``report(key)``: ``cached = cache.get(key)``; se não é ``None``: ``logger.info(f"cache hit: {key}")`` e devolve; senão calcula ``value = compute(key)``,
      ``logger.info(f"calculado: {key}")``, ``cache.set(key, value)`` e devolve. Se ``compute`` levantar uma exceção: ``logger.error(f"falhou: {key}: {NomeDoTipoDoErro}")`` e a exceção
      continua subindo (nada vai para o cache);
    * ``report_and_notify(key, to)``: ``value = self.report(key)``; ``sent = notifier.send(to, f"relatório {key}: {value}")``; se ``not sent``: ``logger.error(f"não enviado para {to}")``;
      devolve ``(value, sent)``.

    Nenhum método pode ter um ``if`` sobre a EXISTÊNCIA de logger, cache ou notificador."""

    def __init__(self, compute, logger=None, cache=None, notifier=None):
        raise NotImplementedError

    def report(self, key):
        raise NotImplementedError

    def report_and_notify(self, key, to):
        raise NotImplementedError
