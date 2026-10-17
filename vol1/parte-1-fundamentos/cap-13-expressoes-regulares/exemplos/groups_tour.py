"""Grupos, nomeados, não capturantes, backreferences, lookaround."""
import re

date = re.search(r"(\d{4})-(\d{2})-(\d{2})", "due 2026-10-12.")
print(date.groups(), date.group(0), date.group(1), date.span(2))

named = re.search(
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", "2026-10-12")
print(named.groupdict())
print(named["year"], named.start("month"), named.end("day"))

# Não capturante: agrupa sem numerar
print(re.findall(r"(?:ab)+(c)", "ababc abc"))
print(re.findall(r"(ab)+(c)", "ababc abc"))   # grupo guarda a última

# Grupo que não participou
m = re.search(r"(a)|(b)", "b")
print(m.groups(), m.group(1))
print(re.search(r"(a)?b", "b").group(1))

# Backreference: palavra repetida
print(re.findall(r"\b(\w+) \1\b", "the the cat sat on on a mat"))
print(re.search(r"(?P<q>['\"]).*?(?P=q)", """say "hi" now""").group())

# Lookaround
print(re.findall(r"\d+(?= reais)", "10 reais, 20 dolares, 30 reais"))
print(re.findall(r"(?<=R\$)\d+", "R$15 e US$20"))
print(re.findall(r"(?<!R\$)\b\d+", "R$15 e US$20 e 7"))
print(re.findall(r"\d+(?!\d|px)", "12px 345 6"))

# Senha: lookaheads em sequência
strong = re.compile(r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}")
print(bool(strong.fullmatch("Abcdefg1")), bool(strong.fullmatch("abcdefg1")))

# Condicional
cond = re.compile(r"(\()?\d{3}(?(1)\))")
print(cond.fullmatch("(123)"), cond.fullmatch("123"), cond.fullmatch("(123"))

# Lookbehind exige largura fixa
try:
    re.compile(r"(?<=a+)b")
except re.PatternError as exc:
    print(type(exc).__name__, exc)

# Grupos atômicos e possessivos (3.11)
print(re.search(r"(?>a+)ab", "aaab"))       # None: o grupo não devolve
print(re.search(r"(?:a+)ab", "aaab"))        # casa por backtracking
print(re.search(r"a++ab", "aaab"))           # None
