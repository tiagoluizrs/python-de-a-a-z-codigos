"""A ordem de try / except / else / finally, e o que `return` faz."""


def flow(kind):
    try:
        print("  try")
        if kind == "err":
            raise ValueError("x")
        if kind == "ret":
            return "retorno do try"
    except ValueError:
        print("  except")
    else:
        print("  else")
    finally:
        print("  finally")
    print("  depois")


for kind in ("ok", "err", "ret"):
    print(kind)
    print(" ->", flow(kind))


# O `else` só roda sem exceção: separa "o que pode falhar" do resto
def parse_positive(text):
    try:
        number = int(text)
    except ValueError:
        return None
    else:
        # Um erro AQUI não será capturado pelo except acima
        return 1 / number


print(parse_positive("4"), parse_positive("abc"))
try:
    parse_positive("0")
except ZeroDivisionError as error:
    print("ZeroDivisionError escapou do else:", error)
