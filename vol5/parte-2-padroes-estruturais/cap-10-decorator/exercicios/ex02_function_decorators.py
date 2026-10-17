"""Exercício 2: quatro decoradores de função (o ``@`` do Python), todos com ``functools.wraps``."""
import time


def retry(times: int, exceptions: tuple = (Exception,), delay: float = 0.0, sleep=time.sleep):
    """Fábrica de decoradores: chama a função até ``times`` vezes (``times >= 1``, senão ``ValueError`` na CRIAÇÃO) enquanto ela levantar uma das
    ``exceptions``; na última tentativa a exceção sobe. Entre uma tentativa e a próxima, ``sleep(delay)`` (só se ``delay > 0``; o ``sleep`` é
    injetável para os testes). Outras exceções sobem na hora. O wrapper expõe ``wrapper.attempts`` com o número de tentativas da ÚLTIMA chamada."""
    raise NotImplementedError


def timed(clock=time.perf_counter):
    """Fábrica de decoradores (use ``@timed()`` com parênteses): cada chamada mede ``clock()`` antes e depois (mesmo se a função levantar uma exceção) e
    acrescenta a duração a ``wrapper.durations`` (uma lista). ``wrapper.last()`` devolve a última duração (``None`` se nunca foi chamada)."""
    raise NotImplementedError


def memoize(fn):
    """Decorador SEM parâmetros: guarda o resultado por argumentos (posicionais e nomeados; os argumentos precisam ser hashable, senão o ``TypeError`` normal
    sobe). ``wrapper.hits`` e ``wrapper.misses`` contam acertos e erros do cache; ``wrapper.cache_clear()`` zera tudo (cache e contadores). Argumentos
    nomeados em ordem diferente (``f(a=1, b=2)`` e ``f(b=2, a=1)``) são a MESMA chamada. Exceções NÃO são guardadas."""
    raise NotImplementedError


def deprecated(message: str, *, warn=None):
    """Fábrica de decoradores: toda chamada emite um ``DeprecationWarning`` com ``f"{fn.__name__} está obsoleta: {message}"`` (``warnings.warn``, com
    ``stacklevel=2``) e depois chama a função. Se ``warn`` for dado, é chamado em vez de ``warnings.warn``, como ``warn(texto)`` (para os testes).
    O wrapper preserva ``__name__``, ``__doc__`` e tem ``__wrapped__``; a docstring original NÃO é alterada."""
    raise NotImplementedError
