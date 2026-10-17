"""A mesma funcionalidade, duas arquiteturas: o que muda no custo de testar, de trocar e de entender."""
import os
import sqlite3
import tempfile
import time
from decimal import Decimal
from pathlib import Path

import archtools
import bola_de_lama
import payment_server
from loja.adapters.http_gateway import HttpPaymentGateway
from loja.adapters.memory import FakeGateway, MemoryInventory, MemoryOrderRepository, RecordingNotifier, StaticPrices
from loja.adapters.sqlite import SqliteOrderRepository
from loja.bootstrap import CATALOG, STOCK
from loja.domain.money import Money
from loja.domain.order import DomainError, Order, OrderLine
from loja.services.place_order import PlaceOrder, PlaceOrderCommand

server, URL = payment_server.start()
work = Path(tempfile.mkdtemp(prefix="arch-"))
CMD = PlaceOrderCommand("ana@exemplo.com", (("CANETA", 4), ("CADERNO", 2)), "VIP10", Decimal("0.10"))


def case_core(repo, gateway):
    return PlaceOrder(repo, gateway, MemoryInventory(STOCK), StaticPrices(CATALOG), RecordingNotifier())


# 1. as duas versões fazem o mesmo?
core_order = case_core(MemoryOrderRepository(), FakeGateway())(CMD)
mud_id, mud_total = bola_de_lama.place_order("ana@exemplo.com", [("CANETA", 4), ("CADERNO", 2)], "0.10", payment_url=URL, db_path=str(work / "mud.db"))
print(f"mesmo total? núcleo {core_order.total()} | bola de lama R$ {mud_total} | iguais: {core_order.total().amount == mud_total}")
for label, call in [("núcleo: pedido de 30 itens", lambda: case_core(MemoryOrderRepository(), FakeGateway())(PlaceOrderCommand("c", (("CANETA", 30),)))),
                    ("bola de lama: pedido de 30 itens", lambda: bola_de_lama.place_order("c", [("CANETA", 30)], payment_url=URL, db_path=str(work / "mud.db")))]:
    try:
        call()
    except (DomainError, ValueError) as error:
        print(f"  {label}: {type(error).__name__}: {error}")


# 2. custo de executar UM teste de cada tipo
def best(fn, n):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e3


def rules_only():                                           # a regra pura: nenhuma porta, nenhum adaptador
    order = Order("o1", "c", [OrderLine("CANETA", 4, Money("2.50")), OrderLine("CADERNO", 2, Money("18.90"))])
    order.place()


sqlite_repo = SqliteOrderRepository(":memory:")
file_repo = SqliteOrderRepository(str(work / "loja.db"))
http_gateway = HttpPaymentGateway(URL)
n_fast, n_slow = 2000, 200
rows = [
    ("regra de domínio pura (Order.place)", best(rules_only, n_fast)),
    ("caso de uso, adaptadores em memória", best(lambda: case_core(MemoryOrderRepository(), FakeGateway())(CMD), n_fast)),
    ("caso de uso, repositório SQLite :memory:", best(lambda: case_core(sqlite_repo, FakeGateway())(CMD), n_fast)),
    ("caso de uso, SQLite em ARQUIVO", best(lambda: case_core(file_repo, FakeGateway())(CMD), n_slow)),
    ("caso de uso, SQLite em arquivo + pagamento HTTP", best(lambda: case_core(file_repo, http_gateway)(CMD), n_slow)),
    ("bola de lama (sqlite em arquivo + HTTP + e-mail)", best(lambda: bola_de_lama.place_order("ana@exemplo.com", [("CANETA", 4), ("CADERNO", 2)], "0.10", payment_url=URL, db_path=str(work / "mud.db")), 5)),
]
print("\ncusto de UM teste:")
base = rows[0][1]
for label, ms in rows:
    print(f"  {label:<52} {ms:9.4f} ms  ({ms / base:9.0f}x a regra pura)")
suite = 400
print(f"\numa suíte de {suite} testes de comportamento: núcleo em memória {rows[1][1] * suite / 1e3:6.2f} s | tudo integrado (arquivo + HTTP) {rows[4][1] * suite / 1e3:6.2f} s | bola de lama {rows[5][1] * suite / 1e3:6.2f} s")


# 3. trocar uma peça: o custo de mudar do repositório em memória para o SQLite
repo_memory, repo_sql = MemoryOrderRepository(), SqliteOrderRepository(":memory:")
for repo in (repo_memory, repo_sql):
    case_core(repo, FakeGateway())(CMD)
a, b = repo_memory.list_for_customer("ana@exemplo.com")[0], repo_sql.list_for_customer("ana@exemplo.com")[0]
print(f"\ntrocar o repositório sem tocar no núcleo: totais iguais? {a.total() == b.total()} | linhas iguais? {len(a.lines) == len(b.lines)}")

# 4. a arquitetura, medida pelo grafo de imports
package = Path(__file__).parent / "loja"
graph = archtools.import_graph(package)
LAYERS = ["domain", "ports", "services", "adapters", "entrypoints"]
print(f"\nmódulos do pacote: {len(graph)} | imports internos: {sum(len(d) for d in graph.values())} | violações da regra de dependência: {archtools.violations(graph, LAYERS)} | ciclos: {archtools.cycles(graph)}")
print("acoplamento (quem depende / de quem depende):")
for module, (afferent, efferent) in sorted(archtools.coupling(graph).items()):
    if afferent or efferent:
        print(f"  {module:<32} aferente {afferent} | eferente {efferent}")

# 5. e a bola de lama no mesmo grafo: tudo importado em um lugar só
import ast

mud = ast.parse(Path(bola_de_lama.__file__).read_text(encoding="utf-8"))
imports = sorted({a.name for n in ast.walk(mud) if isinstance(n, ast.Import) for a in n.names})
print(f"\nbola de lama: 1 função que importa {imports} e mistura regra, rede, banco e e-mail em {len(mud.body[-1].body)} instruções")
server.shutdown()
