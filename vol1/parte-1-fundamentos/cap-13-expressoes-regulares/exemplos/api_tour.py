"""API do módulo re."""
import re

s = "id=42; id=7; name=ana"

# search x match x fullmatch
print(re.search(r"\d+", s))
print(re.match(r"\d+", s))
print(re.prefixmatch(r"id", s))            # 3.15: nome novo de match
print(re.match is re.prefixmatch)
print(re.fullmatch(r"\d+", "123"), re.fullmatch(r"\d+", "123a"))

# findall: devolve strings, tuplas (2+ grupos) ou o grupo (1 grupo)
print(re.findall(r"id=\d+", s))
print(re.findall(r"id=(\d+)", s))
print(re.findall(r"(\w+)=(\w+)", s))

# finditer: objetos Match com posição
for m in re.finditer(r"(?P<k>\w+)=(?P<v>\w+)", s):
    print(m.span(), m["k"], m["v"])

# sub: string, com \g<nome>, função, count
print(re.sub(r"id=(\d+)", r"ID:\1", s))
print(re.sub(r"(?P<k>\w+)=(?P<v>\w+)", r"\g<v>=\g<k>", s))
print(re.sub(r"\d+", lambda m: str(int(m[0]) * 2), s))
print(re.sub(r"id", "X", s, count=1))
print(re.subn(r"id", "X", s))

# Pegadinha: \1 seguido de dígito
print(re.sub(r"(\d)", r"\g<1>0", "5"))
try:
    print(re.sub(r"(\d)", r"\10", "5"))
except re.PatternError as exc:
    print("erro:", exc)

# split
print(re.split(r"[;,]\s*", "a; b,c;  d"))
print(re.split(r"([;,])", "a;b,c"))
print(re.split(r"\s*", "a b"))
print(re.split(r",", "a,b,c,d", maxsplit=2))

# escape
user = "1+1=2 (ok?)"
print(re.escape(user))
print(re.findall(re.escape("1+1"), user))

# Match
m = re.search(r"(?P<a>\d+)-(?P<b>\d+)?", "x 10- y")
print(m.group("a", "b"), m.groups(default=""), m.lastgroup, m.pos, m.re.pattern)
print(m.string, m.expand(r"<\g<a>>"))

# compile e objeto Pattern
pat = re.compile(r"\d+")
print(pat.pattern, pat.flags, pat.groups, pat.findall("1 22"))
print(pat.search("abc 123", 3), pat.fullmatch("xx12", 2))
print(pat.search("abc 123", 5))
print(re.compile(pat) is pat)

# Cache
print(re.compile(r"\d+") is re.compile(r"\d+"))
re.purge()
