"""O adaptador de pagamento por HTTP (um serviço de pagamentos de verdade teria autenticação, idempotência e novas tentativas)."""
import httpx

from loja.domain.money import Money
from loja.ports import PaymentResult


class HttpPaymentGateway:
    def __init__(self, base_url: str, timeout: float = 2.0):
        self.client = httpx.Client(base_url=base_url, timeout=timeout)

    def charge(self, order_id: str, amount: Money) -> PaymentResult:
        response = self.client.post("/charge", json={"order_id": order_id, "amount": str(amount.amount)})
        data = response.json()
        return PaymentResult(approved=data["approved"], reference=data.get("reference", ""), reason=data.get("reason", ""))
