"""Uma refatoração em passos pequenos, com a mesma rede de segurança a cada passo."""
import ast
import itertools
import textwrap


def complexity(source):
    tree = ast.parse(source)
    score = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.IfExp)):
            score += 1
        elif isinstance(node, ast.BoolOp):
            score += len(node.values) - 1
    return score


STEPS = {
    "0 original": """
def invoice_total(items, country, coupon):
    total = 0
    for item in items:
        if item["qty"] > 0:
            if item["price"] > 0:
                total = total + item["qty"] * item["price"]
    if coupon == "TEN":
        total = total - total * 10 / 100
    elif coupon == "FIVE":
        total = total - total * 5 / 100
    if country == "BR":
        total = total + total * 12 / 100
    elif country == "US":
        total = total + total * 7 / 100
    elif country == "DE":
        total = total + total * 19 / 100
    return round(total, 2)
""",
    "1 extrair subtotal": """
def subtotal(items):
    return sum(i["qty"] * i["price"] for i in items if i["qty"] > 0 and i["price"] > 0)

def invoice_total(items, country, coupon):
    total = subtotal(items)
    if coupon == "TEN":
        total = total - total * 10 / 100
    elif coupon == "FIVE":
        total = total - total * 5 / 100
    if country == "BR":
        total = total + total * 12 / 100
    elif country == "US":
        total = total + total * 7 / 100
    elif country == "DE":
        total = total + total * 19 / 100
    return round(total, 2)
""",
    "2 tabelas de regras": """
COUPONS = {"TEN": 10, "FIVE": 5}
TAX = {"BR": 12, "US": 7, "DE": 19}

def subtotal(items):
    return sum(i["qty"] * i["price"] for i in items if i["qty"] > 0 and i["price"] > 0)

def invoice_total(items, country, coupon):
    total = subtotal(items)
    total -= total * COUPONS.get(coupon, 0) / 100
    total += total * TAX.get(country, 0) / 100
    return round(total, 2)
""",
    "3 funções nomeadas": """
COUPONS = {"TEN": 10, "FIVE": 5}
TAX = {"BR": 12, "US": 7, "DE": 19}

def subtotal(items):
    return sum(i["qty"] * i["price"] for i in items if i["qty"] > 0 and i["price"] > 0)

def apply_percent(amount, percent):
    return amount + amount * percent / 100

def invoice_total(items, country, coupon):
    discounted = apply_percent(subtotal(items), -COUPONS.get(coupon, 0))
    return round(apply_percent(discounted, TAX.get(country, 0)), 2)
""",
}

CASES = list(itertools.product(
    [[], [{"qty": 2, "price": 10.0}], [{"qty": 1, "price": 99.99}, {"qty": 0, "price": 5}, {"qty": 3, "price": -1}, {"qty": 4, "price": 2.5}]],
    ["BR", "US", "DE", "AR"], ["TEN", "FIVE", "NONE", None]))

reference = None
print(f"{'passo':<22}{'complexidade':>13}{'linhas':>8}   comportamento")
for name, source in STEPS.items():
    namespace = {}
    exec(textwrap.dedent(source), namespace)
    outputs = [namespace["invoice_total"](*case) for case in CASES]
    reference = reference or outputs
    verdict = "igual ao original" if outputs == reference else "DIVERGE"
    lines = len([l for l in source.strip().splitlines() if l.strip()])
    print(f"{name:<22}{complexity(source):>13}{lines:>8}   {verdict} ({len(CASES)} casos)")
