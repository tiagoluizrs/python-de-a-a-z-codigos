"""`return` dentro de `finally` engole a exceção (PEP 765)."""
import warnings


def swallow():
    try:
        raise RuntimeError("perdida")
    finally:
        return "finally venceu"      # a exceção desaparece


print(swallow())

# O compilador avisa desde o Python 3.14
source = """
def f():
    try:
        pass
    finally:
        return 1
"""
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    compile(source, "<exemplo>", "exec")
print([(w.category.__name__, str(w.message)) for w in caught])


# O jeito certo: o finally limpa, não decide o resultado
def clean_way():
    log = []
    try:
        raise RuntimeError("visível")
    finally:
        log.append("limpeza feita")
        print(log)


try:
    clean_way()
except RuntimeError as error:
    print("a exceção chegou:", error)
