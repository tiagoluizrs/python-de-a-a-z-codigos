"""Arquivos .env: o formato, as armadilhas e a biblioteca python-dotenv."""
import io

from dotenv import dotenv_values

TEXT = """
# comentário
A=1
B="x y"
export C=3
D=${A}_z   # comentário no fim
E='raw \\n não interpreta'
F=
G
H="linha1\\nlinha2"
I=sem aspas # cortado aqui
"""

for key, value in dotenv_values(stream=io.StringIO(TEXT)).items():
    print(f"  {key} = {value!r}")

print("\nobservações:")
print("  - G (sem '=') vira None; F (vazio) vira ''")
print("  - aspas duplas interpretam \\n; aspas simples, não")
print("  - ${A} é expandido a partir do que veio antes")
print("  - TUDO é texto: converta (as_int, as_bool) depois")
print("  - o .env é só uma conveniência de DESENVOLVIMENTO: em produção, o ambiente vem da plataforma")
