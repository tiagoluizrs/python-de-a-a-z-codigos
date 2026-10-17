"""S: Responsabilidade Única. Uma classe deve ter UM motivo para mudar. Como MEDIR isso: a coesão (LCOM4)."""
import ast
import textwrap
from collections import defaultdict

# --- 1. a classe que faz tudo: calcula, formata, grava e envia (quatro motivos para mudar) ---
GOD_CLASS = '''
class OrderReport:
    def __init__(self, orders, path, smtp_host):
        self.orders = orders
        self.path = path
        self.smtp_host = smtp_host

    def total(self):
        return sum(o["price"] * o["qty"] for o in self.orders)

    def by_customer(self):
        totals = {}
        for o in self.orders:
            totals[o["customer"]] = totals.get(o["customer"], 0) + o["price"] * o["qty"]
        return totals

    def to_text(self):
        lines = [f"{c}: {t:.2f}" for c, t in self.by_customer().items()]
        return "\\n".join(lines + [f"TOTAL: {self.total():.2f}"])

    def to_csv(self):
        return "\\n".join(f"{c},{t:.2f}" for c, t in self.by_customer().items())

    def save(self, text):
        with open(self.path, "w") as f:
            f.write(text)

    def send(self, to, text):
        import smtplib
        with smtplib.SMTP(self.smtp_host) as server:
            server.sendmail("relatorios@loja.com", to, text)
'''

# --- 2. a mesma funcionalidade, separada por motivo de mudança ---
REFACTORED = '''
class Sales:
    def __init__(self, orders):
        self.orders = orders

    def total(self):
        return sum(o["price"] * o["qty"] for o in self.orders)

    def by_customer(self):
        totals = {}
        for o in self.orders:
            totals[o["customer"]] = totals.get(o["customer"], 0) + o["price"] * o["qty"]
        return totals


class TextFormatter:
    def render(self, sales):
        lines = [f"{c}: {t:.2f}" for c, t in sales.by_customer().items()]
        return "\\n".join(lines + [f"TOTAL: {sales.total():.2f}"])


class FileStore:
    def __init__(self, path):
        self.path = path

    def save(self, text):
        with open(self.path, "w") as f:
            f.write(text)


class SmtpSender:
    def __init__(self, host):
        self.host = host

    def send(self, to, text):
        import smtplib
        with smtplib.SMTP(self.host) as server:
            server.sendmail("relatorios@loja.com", to, text)
'''


def lcom4(source: str) -> dict[str, int]:
    """LCOM4 por classe: o número de grupos de métodos desconectados. Dois métodos se conectam se usam o MESMO atributo (self.x)
    ou se um chama o outro (self.m()). 1 = coeso; 2 ou mais = a classe faz coisas que não se falam: candidata a ser dividida."""
    result = {}
    for cls in (n for n in ast.walk(ast.parse(textwrap.dedent(source))) if isinstance(n, ast.ClassDef)):
        methods = {m.name: m for m in cls.body if isinstance(m, ast.FunctionDef) and m.name != "__init__"}
        uses: dict[str, set[str]] = {}
        for name, method in methods.items():
            attrs, calls = set(), set()
            for node in ast.walk(method):
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
                    (calls if node.attr in methods else attrs).add(node.attr)
            uses[name] = {("attr", a) for a in attrs} | {("call", c) for c in calls}
        parent = {m: m for m in methods}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        by_resource = defaultdict(list)
        for name, resources in uses.items():
            for kind, what in resources:
                by_resource[what if kind == "call" else ("attr", what)].append(name)
                if kind == "call":
                    parent[find(name)] = find(what)                   # chamar outro método os conecta
        for names in by_resource.values():
            for other in names[1:]:
                parent[find(other)] = find(names[0])
        result[cls.name] = len({find(m) for m in methods})
    return result


print("LCOM4 (grupos de métodos desconectados; 1 = coeso):")
print("  classe que faz tudo ->", lcom4(GOD_CLASS))
print("  depois de dividir   ->", lcom4(REFACTORED))

# --- 3. o CUSTO da mudança: acrescentar um formato novo (CSV) e um novo meio de entrega (um arquivo em S3) ---
print("\nacrescentar o formato CSV:")
print("  na classe que faz tudo: edita OrderReport (já tem 6 métodos e 3 atributos; o teste dela precisa de arquivo e de SMTP)")
print("  na versão dividida: escreve CsvFormatter (uma classe nova, 4 linhas); Sales, FileStore e SmtpSender não são tocadas")

# --- 4. SRP não é "uma classe com um método": é UM MOTIVO para mudar ---
print("\nmotivos para mudar a classe original:")
for reason, who in [("a regra do total (ex.: desconto)", "o financeiro"), ("o formato do relatório", "o marketing"), ("onde guardar", "a infraestrutura"), ("como enviar", "a TI")]:
    print(f"  - {reason:<36} pedida por: {who}")
print("quatro atores diferentes pedem mudanças na MESMA classe: cada mudança arrisca quebrar as outras três")

# --- 5. o perigo do excesso: dividir demais ---
print("\nUMA responsabilidade não é UM método: Sales tem 2 métodos (total, by_customer) porque os dois mudam pelo MESMO motivo")
print("dividir 'total' e 'by_customer' em duas classes só espalharia a regra de negócio por dois arquivos")
