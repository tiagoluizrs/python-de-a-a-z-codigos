"""Flags: IGNORECASE, MULTILINE, DOTALL, VERBOSE, ASCII, NOFLAG."""
import re

print(re.findall(r"python", "Python PYTHON python", re.IGNORECASE))
print(re.findall(r"(?i)python", "Python PYTHON"))
print(re.search(r"(?i:py)thon", "PYthon"), re.search(r"(?i:py)thon", "PYTHON"))

text = "a\nb"
print(re.search(r"a.b", text), re.search(r"a.b", text, re.DOTALL))

# Combinar com |
flags = re.IGNORECASE | re.MULTILINE
print(flags, re.NOFLAG, int(re.NOFLAG))

# Unicode x ASCII
word = "ação 12 ١٢"
print(re.findall(r"\w+", word))
print(re.findall(r"\w+", word, re.ASCII))
print(re.findall(r"\d+", word))
print(re.findall(r"\d+", word, re.ASCII))
print(re.findall(r"[0-9]+", word))
print(re.findall(r"\s", "a\u00a0b\u2003c"), re.findall(r"\s", "a\u00a0b", re.A))
print(re.findall(r"é", "É é", re.I))

# Verbose
phone = re.compile(r"""
    \(?(?P<ddd>\d{2})\)?   # DDD, com ou sem parênteses
    \s*
    (?P<number>9?\d{4}-?\d{4})  # número
""", re.VERBOSE)
print(phone.fullmatch("(11) 98765-4321").groupdict())
print(phone.flags & re.VERBOSE == re.VERBOSE)
