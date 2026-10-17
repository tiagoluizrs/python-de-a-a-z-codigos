"""Formas de capturar: tuplas, `as`, ordem e o nome que desaparece."""
import warnings

# 1. Várias exceções: tupla (ou, desde o 3.14, sem parênteses e sem `as`)
for value in ("12", "x", None):
    try:
        print(int(value))
    except (ValueError, TypeError) as error:
        print(type(error).__name__, "|", error)

source_ok = "try:\n    pass\nexcept TypeError, ValueError:\n    pass\n"
source_as = "try:\n    pass\nexcept TypeError, ValueError as e:\n    pass\n"
compile(source_ok, "<ok>", "exec")
print("sem parênteses e sem `as`: compila (3.14+)")
try:
    compile(source_as, "<as>", "exec")
except SyntaxError as error:
    print("com `as`:", error.msg)

# 2. A ordem importa: o primeiro except compatível vence
try:
    {}["chave"]
except LookupError:
    print("capturado como LookupError (a classe geral veio primeiro)")
except KeyError:
    print("nunca chega aqui")

# 3. O nome da exceção é apagado ao sair do bloco
try:
    1 / 0
except ZeroDivisionError as error:
    pass
try:
    print(error)
except NameError as name_error:
    print("NameError:", name_error)

# 4. `except:` sem classe captura até KeyboardInterrupt e SystemExit
try:
    raise SystemExit(2)
except Exception:
    print("Exception não captura SystemExit")
except BaseException as error:
    print("BaseException capturou:", type(error).__name__)
