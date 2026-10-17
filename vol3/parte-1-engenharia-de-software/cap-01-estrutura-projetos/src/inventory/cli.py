"""Interface de linha de comando: converte argumentos em chamadas ao núcleo."""
import argparse
import sys

from . import __version__, storage
from .core import Item, OutOfStockError


def build_parser():
    parser = argparse.ArgumentParser(prog="inventory", description="Controle de estoque")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--file", default="inventory.json", help="arquivo de dados")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="adiciona itens")
    add.add_argument("sku")
    add.add_argument("name")
    add.add_argument("qty", type=int)
    remove = sub.add_parser("remove", help="retira itens")
    remove.add_argument("sku")
    remove.add_argument("qty", type=int)
    sub.add_parser("list", help="lista o estoque")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    inventory = storage.load(args.file)
    try:
        if args.command == "add":
            inventory.add(Item(args.sku, args.name, args.qty))
        elif args.command == "remove":
            inventory.remove(args.sku, args.qty)
        else:
            for item in inventory.items():
                print(f"{item.sku:<8}{item.name:<20}{item.qty:>5}")
            print(f"total: {inventory.total_quantity()}")
            return 0
    except (OutOfStockError, ValueError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1
    storage.save(inventory, args.file)
    return 0
