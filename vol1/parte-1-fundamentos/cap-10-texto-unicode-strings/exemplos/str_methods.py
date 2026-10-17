"""Passeio pelos métodos de str que valem a pena conhecer bem."""

line = "  name=Ana Paula; city=Recife;; age=31  "
print(line.strip().split(";"))
print([p.strip() for p in line.split(";") if p.strip()])
print("a,b,,c".split(","), "a b  c".split(), "a b  c".split(" "))
print("a,b,c,d".split(",", 1), "a,b,c,d".rsplit(",", 1))
print("l1\nl2\r\nl3\x0bl4\x0cl5 l6".splitlines())
print("l1\nl2\n".splitlines(), "l1\nl2\n".split("\n"))
print("l1\nl2\n".splitlines(keepends=True))

# partition: divide na primeira ocorrência, sempre devolve 3 partes
print("user@example.com".partition("@"))
print("sem-arroba".partition("@"))
print("a.b.c".rpartition("."))

# find vs index vs in
s = "banana"
print(s.find("an"), s.find("x"), s.rfind("an"), s.count("an"),
      s.count("a", 2), "ana" in s)
try:
    s.index("x")
except ValueError as exc:
    print("ValueError:", exc)

# strip remove CONJUNTOS de caracteres, não prefixos
print("www.example.com".strip("w.com"))
print("www.example.com".removeprefix("www.").removesuffix(".com"))
print("xxabcxx".lstrip("x"), "xxabcxx".rstrip("x"))

# startswith/endswith aceitam tupla
print("report.pdf".endswith((".pdf", ".docx")),
      "Mr. Silva".startswith(("Mr.", "Mrs.")))

# replace: com contagem máxima
print("a-b-c-d".replace("-", "+", 2), "abc".replace("", "|"))

# alinhamento e preenchimento
print("[" + "ab".center(8, "*") + "]", "[" + "ab".ljust(5) + "]",
      "[" + "ab".rjust(5, ".") + "]")
print("42".zfill(6), "-42".zfill(6), "+7".zfill(4), "abc".zfill(2))

# maiúsculas e minúsculas
print("python de a a z".title(), "python de a a z".capitalize(),
      "Python".swapcase())
print("they're bill's".title())          # title() erra o apóstrofo
import string
print(string.capwords("they're bill's"))

# tradução em lote
table = str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")
print("Ação, órgão, você".translate(table))
table = str.maketrans({"<": "&lt;", ">": "&gt;", "&": "&amp;"})
print("<b>a & b</b>".translate(table))
print("a1b2c3".translate(str.maketrans("", "", "0123456789")))

# testes de classe
for sample in ["abc", "ab1", "123", "1.5", "", " ", "Ab", "AB"]:
    print(f"{sample!r:6} alpha={sample.isalpha()!s:5} "
          f"digit={sample.isdigit()!s:5} space={sample.isspace()!s:5} "
          f"upper={sample.isupper()!s:5} title={sample.istitle()}")

# juntar
print(", ".join(["a", "b", "c"]), "-".join("abc"), "".join(["x"] * 3))
try:
    ",".join([1, 2])
except TypeError as exc:
    print("TypeError:", exc)
print(",".join(map(str, [1, 2])))
