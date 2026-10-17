"""A MESMA funcionalidade em um arquivo só: lê o pedido, aplica as regras, cobra por HTTP, grava no SQLite e manda o e-mail.

Funciona. O problema aparece quando você precisa TESTAR, TROCAR uma peça ou ler a regra de negócio no meio do resto.
"""
import json
import smtplib
import sqlite3
import uuid
from decimal import Decimal

import httpx

PAYMENT_URL = "http://127.0.0.1:9999"                           # fixo no código
DB_PATH = "loja.db"                                              # fixo no código
PRICES = {"CANETA": "2.50", "CADERNO": "18.90", "MOCHILA": "120.00", "MONITOR": "799.00"}


def place_order(customer, items, coupon_percent=None, payment_url=None, db_path=None):
    total = Decimal("0")
    for sku, qty in items:
        if qty <= 0:
            raise ValueError("quantidade deve ser positiva")
        total += Decimal(PRICES[sku]) * qty
    if sum(q for _, q in items) > 20:
        raise ValueError("no máximo 20 itens por pedido")
    if coupon_percent:
        if not Decimal("0") < Decimal(coupon_percent) <= Decimal("0.50"):
            raise ValueError("cupom inválido")
        total -= total * Decimal(coupon_percent)
    total = total.quantize(Decimal("0.01"))
    if total < Decimal("5.00"):
        raise ValueError("pedido mínimo de R$ 5,00")
    order_id = uuid.uuid4().hex[:8]
    response = httpx.post((payment_url or PAYMENT_URL) + "/charge", json={"order_id": order_id, "amount": str(total)}, timeout=2)
    if not response.json()["approved"]:
        raise ValueError("pagamento recusado")
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.execute("create table if not exists orders (id text, customer text, total text, lines text)")
    conn.execute("insert into orders values (?, ?, ?, ?)", (order_id, customer, str(total), json.dumps(items)))
    conn.commit()
    conn.close()
    try:
        with smtplib.SMTP("localhost", 25, timeout=1) as smtp:
            smtp.sendmail("loja@exemplo.com", customer, f"Pedido {order_id} confirmado: {total}")
    except OSError:
        pass                                                      # e-mail "não crítico": o erro some em silêncio
    return order_id, total
