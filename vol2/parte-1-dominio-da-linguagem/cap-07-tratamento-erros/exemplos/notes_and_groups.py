"""add_note (3.11) e grupos de exceções com except* (3.11)."""
import traceback

# --- add_note: contexto sem trocar a exceção
try:
    try:
        int("abc")
    except ValueError as error:
        error.add_note("ao ler a linha 12 de pedido.csv")
        error.add_note("revise o separador decimal")
        raise
except ValueError as error:
    print(error.__notes__)
    print("".join(traceback.format_exception(error)))


# --- ExceptionGroup: várias falhas independentes ao mesmo tempo
def task(n):
    if n == 1:
        raise ValueError("v1")
    if n == 2:
        raise TypeError("t2")
    if n == 3:
        raise ValueError("v3")


errors = []
for n in range(4):
    try:
        task(n)
    except Exception as error:
        errors.append(error)

group = ExceptionGroup("falhas do lote", errors)
print(group)
print(repr(group))

try:
    raise group
except* ValueError as part:
    print("ValueError group:", part.exceptions)
except* TypeError as part:
    print("TypeError group:", part.exceptions)

# split e subgroup separam sem lançar
matching, rest = group.split(ValueError)
print(matching, "|", rest)
print(group.subgroup(TypeError))

# O que não for tratado continua subindo, como um novo grupo
try:
    try:
        raise group
    except* ValueError:
        print("tratei os ValueError")
except BaseException as leftover:
    print(type(leftover).__name__, leftover.exceptions)

# Regras
try:
    ExceptionGroup("x", [KeyboardInterrupt()])
except TypeError as error:
    print("TypeError:", error)
base = BaseExceptionGroup("g", [KeyboardInterrupt(), ValueError("v")])
print(type(base).__name__)
try:
    ExceptionGroup("x", [])
except ValueError as error:
    print("ValueError:", error)

# except* com uma exceção simples: ela é embrulhada em um grupo
try:
    try:
        raise ValueError("solto")
    except* ValueError as part:
        print(repr(part))
except BaseException:
    pass
