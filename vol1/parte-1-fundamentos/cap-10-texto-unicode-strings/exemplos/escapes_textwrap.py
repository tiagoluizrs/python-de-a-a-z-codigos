"""Escapes, raw strings, textwrap, string.Template e imutabilidade."""
import re
import string
import sys
import textwrap

# escapes
print("tab:\t|nl:\\n|aspas: \" '|unicode: \u00e9 \U0001F600 \N{DEGREE SIGN}")
print("\x41\101\u0041", len("\0"), repr("a\
b"))                                   # barra no fim da linha: continua
print(repr("""linha 1
linha 2"""), "implícita " "concatenação")

# raw strings: a barra invertida fica como está
print(r"C:\novo\teste", len(r"\n"), len("\n"))
print(r"\d+\.\d+")
print(re.findall(r"\d+", "a12b345"))
print(repr(r"\""), r"termina com barra: \\")
# r"\" é erro de sintaxe: a barra escapa a aspa final
try:
    compile('r"\\"', "<demo>", "eval")
except SyntaxError as exc:
    print("SyntaxError:", exc.msg)

# bytes literais e f-strings brutas
print(rb"\x00", fr"\d{{3}}-{2 + 2}")

# textwrap
paragraph = ("Python é uma linguagem de programação de alto nível, "
             "interpretada e de propósito geral, criada por Guido.")
print(textwrap.fill(paragraph, width=40))
print(textwrap.shorten(paragraph, width=45, placeholder="..."))
print(textwrap.indent("a\nb\n\nc", "> "))
code = """
    def f():
        return 1
"""
print(repr(textwrap.dedent(code)))
print(textwrap.fill(paragraph, width=30, initial_indent="* ",
                    subsequent_indent="  "))

# string.Template: substituição simples, segura para entrada de usuário
tpl = string.Template("Olá, $name! Você tem $$${amount}.")
print(tpl.substitute(name="Ana", amount=10))
print(tpl.safe_substitute(name="Ana"))
try:
    tpl.substitute(name="Ana")
except KeyError as exc:
    print("KeyError:", exc)
print(string.ascii_lowercase, string.digits, repr(string.whitespace))
print(string.punctuation)

# imutabilidade: toda "modificação" cria outro objeto
s = "abc"
t = s.upper()
print(s, t, s is t)
try:
    s[0] = "X"
except TypeError as exc:
    print("TypeError:", exc)
print(sys.getsizeof("a" * 10), sys.getsizeof("é" * 10),
      sys.getsizeof("你" * 10), sys.getsizeof("😀" * 10))
