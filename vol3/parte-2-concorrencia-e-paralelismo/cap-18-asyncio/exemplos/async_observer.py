"""O padrão Observer com assinantes assíncronos (promessa do Capítulo 7)."""
import asyncio
import time


class EventBus:
    """Publica eventos para assinantes ``async def``, cada um isolado dos demais."""

    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event, handler):
        self._subscribers.setdefault(event, []).append(handler)

    async def publish(self, event, payload):
        handlers = self._subscribers.get(event, [])
        results = await asyncio.gather(*(h(payload) for h in handlers), return_exceptions=True)
        return [r for r in results if isinstance(r, Exception)]     # as falhas voltam; ninguém derruba ninguém


async def send_email(order):
    await asyncio.sleep(0.1)
    print(f"  e-mail do pedido {order['id']} enviado")


async def update_stock(order):
    await asyncio.sleep(0.05)
    raise RuntimeError("estoque indisponível")


async def audit(order):
    await asyncio.sleep(0.02)
    print(f"  auditoria do pedido {order['id']} registrada")


async def main():
    bus = EventBus()
    for handler in (send_email, update_stock, audit):
        bus.subscribe("order_created", handler)
    start = time.perf_counter()
    errors = await bus.publish("order_created", {"id": 7})
    print(f"3 assinantes (0,10 + 0,05 + 0,02 s) notificados em {time.perf_counter() - start:.2f} s; falhas isoladas: {[str(e) for e in errors]}")


asyncio.run(main())
