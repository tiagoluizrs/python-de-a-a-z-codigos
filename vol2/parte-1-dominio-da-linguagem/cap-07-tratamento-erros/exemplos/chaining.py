"""Encadeamento: `raise ... from`, contexto implícito e `from None`."""
import traceback


def load_explicit():
    try:
        int("x")
    except ValueError as error:
        raise RuntimeError("configuração inválida") from error


def load_implicit():
    try:
        {}["k"]
    except KeyError:
        raise ValueError("outro erro")        # sem `from`


def load_hidden():
    try:
        {}["k"]
    except KeyError:
        raise ValueError("sem contexto") from None


for func in (load_explicit, load_implicit, load_hidden):
    try:
        func()
    except Exception as error:
        print(f"{func.__name__}: __cause__={error.__cause__!r}")
        print(f"{'':{len(func.__name__) + 2}}__context__={error.__context__!r}")
        print(f"{'':{len(func.__name__) + 2}}__suppress_context__="
              f"{error.__suppress_context__}")
        if func is not load_hidden:
            print("".join(traceback.format_exception(error)))
