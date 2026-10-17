"""Uso de if __name__ == "__main__" (detalhes no Capítulo 3 do Volume 2)."""


def main() -> None:
    print("executando como script")


print("__name__ =", __name__)

if __name__ == "__main__":
    main()
