"""O CPython compila o código-fonte para bytecode antes de executar."""
import dis


def add_tax(price, rate):
    return price * (1 + rate)


# Instruções que a máquina virtual executa de fato
dis.dis(add_tax)

# O código compilado é um objeto como qualquer outro
code = add_tax.__code__
print("\nco_varnames :", code.co_varnames)
print("co_consts   :", code.co_consts)
print("bytecode    :", code.co_code.hex(" "))
