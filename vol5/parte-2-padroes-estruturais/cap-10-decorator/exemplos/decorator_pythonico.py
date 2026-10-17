"""Decorator em Python: a sintaxe @ embrulha FUNÇÕES e CLASSES; o decorador de objetos do GoF continua existindo, e a biblioteca padrão o usa nos fluxos de E/S."""
import asyncio
import functools
import gzip
import inspect
import io
import time


# --- 1. o decorador de função: o padrão em 8 linhas ---
def logged(fn):
    @functools.wraps(fn)                                       # preserva __name__, __doc__, __wrapped__, a assinatura
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return fn(*args, **kwargs)

    wrapper.calls = 0
    return wrapper


@logged
def add(a, b):
    """Soma dois números."""
    return a + b


add(1, 2)
add(3, 4)
print("decorador de função:", add.calls, "chamadas | nome:", add.__name__, "| doc:", add.__doc__, "| assinatura:", inspect.signature(add), "| original:", add.__wrapped__.__name__)


def no_wraps(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


@no_wraps
def sub(a, b):
    """Subtrai."""
    return a - b


print("sem functools.wraps:", sub.__name__, "| doc:", sub.__doc__, "(o decorador 'apaga' a identidade da função)")


# --- 2. com parâmetros: a fábrica de decoradores (uma função a mais) ---
def retry(times, exceptions=(Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
        return wrapper
    return decorator


attempts = []


@retry(3, exceptions=(ConnectionError,))
def flaky():
    attempts.append(1)
    if len(attempts) < 3:
        raise ConnectionError("caiu")
    return "ok"


print("\n@retry(3):", flaky(), "depois de", len(attempts), "tentativas")

# --- 3. a ORDEM: @a @b def f  equivale a  f = a(b(f)) ---
trace = []


def label(name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            trace.append(f"entra {name}")
            result = fn(*args, **kwargs)
            trace.append(f"sai {name}")
            return result
        return wrapper
    return decorator


@label("A")
@label("B")
def work():
    trace.append("trabalho")


work()
print("\n@A @B def work:", " -> ".join(trace), "| o decorador de CIMA é o mais EXTERNO")

# --- 4. decorar classes: o mesmo mecanismo, recebendo e devolvendo uma classe ---
def auto_repr(cls):
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in sorted(vars(self).items()))
        return f"{cls.__name__}({fields})"
    cls.__repr__ = __repr__
    return cls


@auto_repr
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y


print("\ndecorador de classe:", Point(1, 2))

# --- 5. o decorador de OBJETOS do GoF continua aqui: a biblioteca padrão empilha fluxos de E/S ---
raw = io.BytesIO()
stack = io.TextIOWrapper(gzip.GzipFile(fileobj=raw, mode="wb"), encoding="utf-8")        # texto -> bytes -> gzip -> memória
stack.write("olá, mundo! " * 100)
stack.close()
print(f"\nTextIOWrapper(GzipFile(BytesIO)): 1200 caracteres viraram {len(raw.getvalue())} bytes comprimidos, cada camada com a MESMA interface de arquivo")
print("o decorador de função (@) muda UMA função na hora da definição; o decorador de objeto empilha camadas por instância, em tempo de execução")


# --- 6. decoradores e async: o wrapper precisa ser async também ---
def timed_async(fn):
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return await fn(*args, **kwargs)
        finally:
            wrapper.last = time.perf_counter() - start
    return wrapper


@timed_async
async def pause():
    await asyncio.sleep(0.02)
    return "feito"


print("decorador async:", asyncio.run(pause()), f"em {pause.last * 1000:.0f} ms | é coroutine function?", inspect.iscoroutinefunction(pause))


# --- 7. o custo ---
def best(fn, n=300_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


def plain(x):
    return x


def passthrough(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


one = passthrough(plain)
three = passthrough(passthrough(passthrough(plain)))
print("\ncusto de chamar uma função:")
for label_, fn in [("sem decorador", lambda: plain(1)), ("1 decorador", lambda: one(1)), ("3 decoradores empilhados", lambda: three(1))]:
    print(f"  {label_:<26} {best(fn):5.0f} ns")


@functools.lru_cache(maxsize=None)
def fib_cached(n):
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)


def fib_plain(n):
    return n if n < 2 else fib_plain(n - 1) + fib_plain(n - 2)


start = time.perf_counter()
fib_plain(25)
t_plain = time.perf_counter() - start
start = time.perf_counter()
fib_cached(25)
t_cached = time.perf_counter() - start
print(f"\nfib(25) sem cache {t_plain * 1000:7.1f} ms | com @lru_cache {t_cached * 1e6:7.1f} µs | {t_plain / t_cached:,.0f}x mais rápido: o decorador de cache é o que mais paga o custo da chamada extra")
