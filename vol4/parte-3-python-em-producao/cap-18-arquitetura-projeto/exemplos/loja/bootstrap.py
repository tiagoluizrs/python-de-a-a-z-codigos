"""A RAIZ DE COMPOSIÇÃO: o único lugar que conhece as implementações concretas e as liga ao núcleo."""
import os

from loja.adapters.memory import FakeGateway, MemoryInventory, MemoryOrderRepository, RecordingNotifier, StaticPrices
from loja.domain.money import Money
from loja.services.place_order import PlaceOrder

CATALOG = {"CANETA": Money("2.50"), "CADERNO": Money("18.90"), "MOCHILA": Money("120.00"), "MONITOR": Money("799.00")}
STOCK = {"CANETA": 500, "CADERNO": 200, "MOCHILA": 30, "MONITOR": 5}


def build(env: dict | None = None):
    """Monta o caso de uso conforme a configuração (``LOJA_REPO=memory|sqlite``, ``LOJA_PAYMENT_URL``)."""
    env = os.environ if env is None else env
    if env.get("LOJA_REPO", "memory") == "sqlite":
        from loja.adapters.sqlite import SqliteOrderRepository          # import tardio: só quem usa paga
        repo = SqliteOrderRepository(env.get("LOJA_DB", ":memory:"))
    else:
        repo = MemoryOrderRepository()
    if env.get("LOJA_PAYMENT_URL"):
        from loja.adapters.http_gateway import HttpPaymentGateway
        gateway = HttpPaymentGateway(env["LOJA_PAYMENT_URL"])
    else:
        gateway = FakeGateway()
    notifier = RecordingNotifier()
    use_case = PlaceOrder(repo, gateway, MemoryInventory(STOCK), StaticPrices(CATALOG), notifier)
    return use_case, repo, notifier
