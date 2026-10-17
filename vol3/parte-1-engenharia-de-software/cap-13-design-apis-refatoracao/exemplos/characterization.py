"""Testes de caracterização: capturar o comportamento ATUAL antes de refatorar."""
import itertools


def shipping_legacy(weight, country, express, member):
    """Código antigo, sem testes, ninguém lembra as regras exatas."""
    if country == "BR":
        if weight < 1:
            r = 10
        elif weight < 5:
            r = 18
        else:
            r = 50
        if express:
            r = r * 2 if weight >= 5 else r + 10
        if member and not express and weight >= 5:
            r = 25
    elif country == "US":
        if weight < 1:
            r = 30
        else:
            r = 60
        if express:
            r += 20
    else:
        return None
    return r


INPUTS = list(itertools.product([0.5, 1, 4.9, 5, 20], ["BR", "US", "AR"], [False, True], [False, True]))


def capture(func):
    """O "golden master": a saída (ou a exceção) para cada entrada."""
    master = {}
    for args in INPUTS:
        try:
            master[args] = func(*args)
        except Exception as error:                      # noqa: BLE001
            master[args] = f"{type(error).__name__}: {error}"
    return master


golden = capture(shipping_legacy)
print(f"{len(golden)} comportamentos capturados; exemplos:", [list(golden.values())[i] for i in (0, 7, 40, 59)])

# Refatoração: tabela + regras explícitas
RATES = {("BR", "light"): 10, ("BR", "medium"): 18, ("BR", "heavy"): 50, ("US", "light"): 30, ("US", "medium"): 60, ("US", "heavy"): 60}


def band(weight):
    return "light" if weight < 1 else "medium" if weight < 5 else "heavy"


def shipping_new(weight, country, express, member):
    base = RATES.get((country, band(weight)))
    if base is None:
        return None
    if country == "BR":
        if express:
            return base * 2 if band(weight) == "heavy" else base + 10
        return 25 if member and band(weight) == "heavy" else base
    return base + 20 if express else base


new = capture(shipping_new)
differences = {args: (golden[args], new[args]) for args in INPUTS if golden[args] != new[args]}
print("diferenças entre o antigo e o refatorado:", differences or "nenhuma")

# A rede de segurança pega o erro: uma "refatoração" que mudou uma regra sem querer
def shipping_wrong(weight, country, express, member):
    result = shipping_new(weight, country, express, member)
    return result + 1 if result and member else result


wrong = capture(shipping_wrong)
bad = [args for args in INPUTS if golden[args] != wrong[args]]
print(f"a versão com um erro sutil diverge em {len(bad)} de {len(INPUTS)} entradas; a primeira: {bad[0]}")
