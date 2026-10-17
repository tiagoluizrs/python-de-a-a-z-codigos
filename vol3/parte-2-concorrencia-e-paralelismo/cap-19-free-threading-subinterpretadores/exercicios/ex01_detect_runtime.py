"""Exercício 1: descobrir em que tipo de Python o código está rodando."""


def detect_runtime():
    """Devolve um dicionário com:

    * ``"free_threaded_build"``: ``True`` se o interpretador foi COMPILADO sem GIL
      (``sysconfig.get_config_var("Py_GIL_DISABLED")`` verdadeiro);
    * ``"gil_enabled"``: ``True`` se o GIL está ativo AGORA (``sys._is_gil_enabled()``;
      em versões sem essa função, considere ``True``);
    * ``"parallel_threads"``: ``True`` se threads de Python podem executar em
      paralelo (build sem GIL E GIL desligado agora);
    * ``"version"``: ``(major, minor)`` de ``sys.version_info``."""
    raise NotImplementedError


def describe_runtime(info):
    """Texto de uma linha para ``info`` (o dicionário de ``detect_runtime``):
    ``"Python 3.15 (build com GIL)"``, ``"Python 3.15 (build sem GIL, GIL desligado)"``
    ou ``"Python 3.15 (build sem GIL, GIL religado)"``."""
    raise NotImplementedError
