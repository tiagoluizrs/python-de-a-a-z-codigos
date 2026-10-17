"""Modulo que importa um irmao e tambem pode rodar como script."""
from .helpers import greet


def main() -> None:
    print(greet("world"))
    print("__name__ =", __name__, "| __package__ =", __package__)


if __name__ == "__main__":
    main()
