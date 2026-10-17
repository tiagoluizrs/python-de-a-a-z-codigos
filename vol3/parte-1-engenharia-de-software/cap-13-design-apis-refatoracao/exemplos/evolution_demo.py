"""Mudanças compatíveis e incompatíveis em uma assinatura, vistas por quem JÁ usa a função."""
import inspect


def v1(url, timeout):
    return (url, timeout)


# Compatível: acrescentar parâmetro COM padrão, só-nomeado
def v2_ok(url, timeout, *, retries=3):
    return (url, timeout, retries)


# Quebra: parâmetro novo OBRIGATÓRIO
def v2_required(url, timeout, retries):
    return (url, timeout, retries)


# Quebra: reordenar parâmetros posicionais
def v2_reordered(timeout, url):
    return (url, timeout)


# Quebra: renomear parâmetro (afeta quem usa por nome)
def v2_renamed(url, seconds):
    return (url, seconds)


# Quebra: tornar só-nomeado o que era posicional
def v2_kwonly(url, *, timeout):
    return (url, timeout)

old_calls = [lambda f: f("http://x", 5), lambda f: f("http://x", timeout=5), lambda f: f(url="http://x", timeout=5)]
labels = ["posicional", "timeout=", "tudo por nome"]
print(f"{'versão nova':<16}" + "".join(f"{l:>16}" for l in labels))
for fn in (v2_ok, v2_required, v2_reordered, v2_renamed, v2_kwonly):
    row = []
    for call in old_calls:
        try:
            call(fn)
            row.append("ok")
        except TypeError:
            row.append("QUEBRA")
    print(f"{fn.__name__:<16}" + "".join(f"{r:>16}" for r in row))

print()
for fn in (v1, v2_ok, v2_kwonly):
    print(f"  {fn.__name__}{inspect.signature(fn)}")
