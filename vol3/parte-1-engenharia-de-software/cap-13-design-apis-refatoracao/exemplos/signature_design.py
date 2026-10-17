"""Assinaturas: o que a forma de uma função convida (ou impede) o usuário a fazer."""
import inspect
from dataclasses import dataclass, replace


# 1) Parâmetro booleano posicional: a chamada não se lê
def render_bad(page, True_=False, False_=True):
    return (page, True_, False_)


print("render(page, True, False) diz o quê?  ->  impossível saber sem abrir a função")


# 2) Argumentos só-nomeados: o ponto de chamada documenta
def render(page, *, minify=False, cache=True):
    return (page, minify, cache)


print("render('p', minify=True) ->", render("p", minify=True))
try:
    render("p", True)
except TypeError as error:
    print("render('p', True) ->", "TypeError:", error)

# 3) Só-posicionais: liberdade para renomear sem quebrar ninguém
def clamp(value, low, high, /):
    return max(low, min(value, high))


print("clamp(5, 0, 3) =", clamp(5, 0, 3))
try:
    clamp(value=5, low=0, high=3)
except TypeError as error:
    print("clamp(value=5, ...) ->", "TypeError:", error)

# 4) Padrão mutável: a armadilha do Capítulo 9 do Volume 1, agora como erro de design
def add_bad(item, bucket=[]):
    bucket.append(item)
    return bucket


def add(item, bucket=None):
    bucket = [] if bucket is None else bucket
    return [*bucket, item]


add_bad(1)
print("add_bad(2) ->", add_bad(2), "| add(2) ->", add(2))

# 5) Muitos parâmetros: um objeto de opções
@dataclass(frozen=True)
class Options:
    timeout: float = 10.0
    retries: int = 3
    verify: bool = True
    headers: tuple = ()

    def with_(self, **changes):
        return replace(self, **changes)


def fetch(url, *, options=Options()):
    return (url, options)


base = Options(retries=5)
print("fetch(...) com opções reaproveitáveis:", fetch("http://x", options=base.with_(timeout=1.0)))

# 6) O mesmo parâmetro, nomes diferentes: a inconsistência custa
print("consistência: use sempre 'timeout', e não 'timeout' aqui, 'time_limit' ali e 'max_wait' lá")

# 7) O que a assinatura revela
for fn in (render, clamp, fetch):
    print(f"  {fn.__name__}{inspect.signature(fn)}")
