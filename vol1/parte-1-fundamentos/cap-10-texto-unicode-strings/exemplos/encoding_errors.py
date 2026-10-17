"""Erros de codificação, handlers e mojibake."""

text = "ação 😀"
for handler in ("strict", "ignore", "replace", "xmlcharrefreplace",
                "backslashreplace", "namereplace"):
    try:
        print(f"{handler:18}", text.encode("ascii", errors=handler))
    except UnicodeEncodeError as exc:
        print(f"{handler:18} UnicodeEncodeError: {exc}")

raw = "ação".encode("utf-8")
print(raw)
for handler in ("strict", "replace", "ignore", "backslashreplace",
                "surrogateescape"):
    try:
        print(f"{handler:16}", ascii(raw.decode("ascii", errors=handler)))
    except UnicodeDecodeError as exc:
        print(f"{handler:16} UnicodeDecodeError: {exc}")

# o atributo do erro diz exatamente onde e por quê
try:
    b"caf\xe9".decode("utf-8")
except UnicodeDecodeError as exc:
    print(exc.encoding, exc.start, exc.end, exc.reason, exc.object)

# mojibake: bytes UTF-8 lidos como Latin-1 (e como cp1252)
original = "Ação, coração e não"
garbled = original.encode("utf-8").decode("latin-1")
print(garbled)
print(garbled.encode("latin-1").decode("utf-8"))   # conserto
print(original.encode("utf-8").decode("cp1252", errors="replace"))

# o inverso: bytes Latin-1 lidos como UTF-8
latin = "coração".encode("latin-1")
print(latin.decode("utf-8", errors="replace"))

# codificação errada quase nunca falha em Latin-1 (todo byte é válido)
print(bytes(range(256)).decode("latin-1") is not None)
try:
    bytes(range(256)).decode("utf-8")
except UnicodeDecodeError as exc:
    print("utf-8 rejeita:", exc.reason)

# handler próprio
import codecs

def to_question_mark(exc):
    if isinstance(exc, UnicodeEncodeError):
        n = exc.end - exc.start
        return ("?" * n, exc.end)
    raise exc

codecs.register_error("qmark", to_question_mark)
print("ação 😀".encode("ascii", errors="qmark"))
