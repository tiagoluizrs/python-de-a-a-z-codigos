"""Decoradores de produção: timer, retry, cache com TTL, log,
controle de acesso, registro de plugins e depreciação."""
import functools
import logging
import time
import warnings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("demo")


# 1. timer: mede o tempo com um relógio monotônico
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            log.info("%s took %.1f ms", func.__name__, elapsed * 1e3)
    return wrapper


# 2. retry com backoff exponencial
def retry(times=3, exceptions=(Exception,), delay=0.01, backoff=2.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == times:
                        raise
                    log.warning("%s failed (%s), attempt %d/%d",
                                func.__name__, exc, attempt, times)
                    time.sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator


# 3. cache com TTL (usa um relógio injetável para ser testável)
def ttl_cache(seconds, clock=time.monotonic):
    def decorator(func):
        store = {}   # chave -> (expira_em, valor)

        @functools.wraps(func)
        def wrapper(*args):
            now = clock()
            hit = store.get(args)
            if hit is not None and hit[0] > now:
                return hit[1]
            value = func(*args)
            store[args] = (now + seconds, value)
            return value

        wrapper.cache_clear = store.clear
        return wrapper
    return decorator


# 4. log de chamadas (argumentos, resultado, exceção)
def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        shown = ", ".join([repr(a) for a in args]
                          + [f"{k}={v!r}" for k, v in kwargs.items()])
        log.info("-> %s(%s)", func.__name__, shown)
        try:
            result = func(*args, **kwargs)
        except Exception:
            log.exception("!! %s raised", func.__name__)
            raise
        log.info("<- %s returned %r", func.__name__, result)
        return result
    return wrapper


# 5. controle de acesso
class PermissionDenied(Exception):
    pass


def require_role(role):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(user, *args, **kwargs):
            if role not in user.get("roles", ()):
                raise PermissionDenied(f"{user['name']} needs {role!r}")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator


# 6. registro de plugins: o decorador devolve a própria função
HANDLERS = {}


def register(name):
    def decorator(func):
        if name in HANDLERS:
            raise ValueError(f"duplicate handler: {name}")
        HANDLERS[name] = func
        return func          # sem wrapper: custo zero na chamada
    return decorator


# 7. depreciação
def deprecated(reason):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(f"{func.__name__} is deprecated: {reason}",
                          DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------
@timer
def slow_sum(n):
    time.sleep(0.02)
    return sum(range(n))


print(slow_sum(1000))

attempts = []


@retry(times=3, exceptions=(ConnectionError,))
def flaky():
    attempts.append(1)
    if len(attempts) < 3:
        raise ConnectionError("network down")
    return "ok"


print(flaky(), len(attempts))


@retry(times=2, exceptions=(ConnectionError,))
def wrong_kind():
    raise ValueError("not retried")


try:
    wrong_kind()
except ValueError as exc:
    print("ValueError:", exc)

now = [0.0]


@ttl_cache(10, clock=lambda: now[0])
def lookup(key):
    print("  real lookup", key)
    return key.upper()


print(lookup("a"), lookup("a"))
now[0] = 11.0
print(lookup("a"))


@log_calls
def divide(a, b=1):
    return a / b


divide(6, b=3)
try:
    divide(1, 0)
except ZeroDivisionError:
    pass


@require_role("admin")
def delete_user(user, target):
    return f"{user['name']} deleted {target}"


print(delete_user({"name": "ana", "roles": ["admin"]}, "bob"))
try:
    delete_user({"name": "eve", "roles": []}, "bob")
except PermissionDenied as exc:
    print("PermissionDenied:", exc)


@register("csv")
def handle_csv(text):
    return text.split(",")


@register("tsv")
def handle_tsv(text):
    return text.split("\t")


print(sorted(HANDLERS), HANDLERS["csv"]("a,b"))


@deprecated("use new_api() instead")
def old_api():
    return 1


with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    old_api()
w = caught[0]
print(w.category.__name__, w.message, w.filename.endswith(".py"),
      w.lineno)
