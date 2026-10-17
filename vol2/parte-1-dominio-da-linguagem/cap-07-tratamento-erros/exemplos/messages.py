"""As mensagens reais das exceções mais comuns."""
import errno


def show(label, func):
    try:
        func()
    except Exception as error:
        print(f"{label:<14}{type(error).__name__}: {error}")


show("índice", lambda: [][0])
show("chave", lambda: {}["a"])
show("conversão", lambda: int("x"))
show("atributo", lambda: None.foo)
show("tipo", lambda: 1 + "1")
show("divisão", lambda: 1 / 0)
show("nome", lambda: undefined_name)
show("chamada", lambda: len())
show("desempacotar", lambda: (lambda a, b: a)(*[1]))
show("iteração", lambda: next(iter([])))
show("hash", lambda: {[]: 1})
show("recursão", lambda: (lambda f: f(f))(lambda f: f(f)))
try:
    assert 1 > 2, "falhou"
except AssertionError as error:
    print("assert        AssertionError:", error)
print(str(KeyError("chave")), "<- repr da chave, não o texto")
