"""Um ponto de entrada (a CLI). Converte argumentos em um comando e o resultado em texto: nenhuma regra de negócio aqui."""
import argparse
import sys
from decimal import Decimal

from loja.bootstrap import build
from loja.domain.order import DomainError
from loja.services.place_order import PlaceOrderCommand


def main(argv: list[str] | None = None, env: dict | None = None) -> int:
    parser = argparse.ArgumentParser(prog="loja")
    parser.add_argument("customer")
    parser.add_argument("items", nargs="+", metavar="SKU:QTD")
    parser.add_argument("--coupon", metavar="CODIGO=PERCENTUAL")
    args = parser.parse_args(argv)
    items = tuple((sku, int(qty)) for sku, qty in (item.split(":") for item in args.items))
    code, percent = (args.coupon.split("=") if args.coupon else (None, None))
    place_order, _, _ = build(env)
    try:
        order = place_order(PlaceOrderCommand(args.customer, items, code, Decimal(percent) if percent else None))
    except DomainError as error:
        print(f"loja: {error}", file=sys.stderr)
        return 1
    print(f"pedido {order.id} confirmado: {order.total()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
