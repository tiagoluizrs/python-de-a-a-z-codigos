"""Um passeio pelo bytecode do 3.15 e pelo objeto de código."""
import dis


def add(a, b):
    c = a + b
    return c * 2


dis.dis(add)
code = add.__code__
print("bytes:", code.co_code[:8], "...")
print("consts:", code.co_consts, "| names:", code.co_names, "| varnames:", code.co_varnames)
print("pilha máx:", code.co_stacksize, "| locais:", code.co_nlocals, "| args:", code.co_argcount)
print("linhas:", list(code.co_lines()))

# Dobramento de constantes: o compilador calcula o que pode
print(compile("x = 2 * 3 + 1", "<c>", "exec").co_consts)
print([i.opname for i in dis.get_instructions(compile("x = 2 * 3 + 1", "<c>", "exec"))])


# Código morto: o compilador remove o corpo do if False
def dead():
    if False:
        print("nunca")
    return 1


print([i.opname for i in dis.get_instructions(dead)])


# Closures: variáveis capturadas viram células
def outer():
    x = 1

    def inner():
        return x

    return inner


print(outer.__code__.co_cellvars, outer().__code__.co_freevars)
print([i.opname for i in dis.get_instructions(outer)][:6])


# try/except sem custo no caminho feliz: a tabela de exceções fica FORA do bytecode
def safe(a):
    try:
        return 1 / a
    except ZeroDivisionError:
        return 0


ops = [i.opname for i in dis.get_instructions(safe)]
print("instruções com SETUP/TRY:", [o for o in ops if "SETUP" in o or o == "TRY"], "| tabela:", len(safe.__code__.co_exceptiontable), "bytes")


# Compreensões são embutidas na função (desde o 3.12): sem objeto de função extra
def squares(n):
    return [i * i for i in range(n)]


print("MAKE_FUNCTION na compreensão?", any(i.opname == "MAKE_FUNCTION" for i in dis.get_instructions(squares)))

# Código dentro de código: funções aninhadas vivem em co_consts
import types
print([c.co_name for c in outer.__code__.co_consts if isinstance(c, types.CodeType)])
