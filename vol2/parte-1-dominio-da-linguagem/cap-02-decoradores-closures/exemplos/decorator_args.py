"""Decoradores com argumentos, empilhamento e uso com/sem parênteses."""
import functools


def repeat(times):
    """Fábrica de decoradores: três níveis."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


@repeat(3)
def hello():
    print("hello")


hello()
# @repeat(3) equivale a: hello = repeat(3)(hello)


# Esquecer os parênteses
@repeat
def oops():
    pass


print(type(oops).__name__, oops.__name__)
try:
    oops()
except TypeError as exc:
    print("TypeError:", exc)


# Empilhamento: a ordem importa
def tag(name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"enter {name}")
            try:
                return func(*args, **kwargs)
            finally:
                print(f"exit {name}")
        return wrapper
    return decorator


@tag("A")
@tag("B")
def work():
    print("working")


work()
# equivale a work = tag("A")(tag("B")(work))
print(work.__wrapped__.__wrapped__.__name__)


# Com e sem parênteses
def flexible(func=None, *, label="call"):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            print(f"[{label}] {fn.__name__}")
            return fn(*args, **kwargs)
        return wrapper

    if func is None:          # usado como @flexible(label="x")
        return decorator
    return decorator(func)    # usado como @flexible


@flexible
def a():
    return 1


@flexible(label="custom")
def b():
    return 2


@flexible()
def c():
    return 3


print(a(), b(), c())


# Decorador em método: o primeiro argumento é self
def log_method(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"{type(self).__name__}.{func.__name__}", list(args))
        return func(self, *args, **kwargs)
    return wrapper


class Account:
    def __init__(self):
        self.balance = 0

    @log_method
    def deposit(self, amount):
        self.balance += amount
        return self.balance


print(Account().deposit(10))
