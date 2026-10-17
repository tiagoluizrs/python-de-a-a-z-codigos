"""Quantos bytes cada ponto de código ocupa em cada codificação."""

samples = ["A", "é", "€", "你", "😀"]
print(f"{'char':5}{'U+':>9}{'utf-8':>7}{'utf-16-le':>11}"
      f"{'utf-32-le':>11}{'latin-1':>9}{'ascii':>7}")


def size(ch, enc):
    try:
        return len(ch.encode(enc))
    except UnicodeEncodeError:
        return "-"


for ch in samples:
    print(f"{ch:5}{ord(ch):>9X}{size(ch, 'utf-8'):>7}"
          f"{size(ch, 'utf-16-le'):>11}{size(ch, 'utf-32-le'):>11}"
          f"{size(ch, 'latin-1'):>9}{size(ch, 'ascii'):>7}")

# fronteiras exatas das faixas do UTF-8
for cp in (0x7F, 0x80, 0x7FF, 0x800, 0xFFFF, 0x10000, 0x10FFFF):
    b = chr(cp).encode("utf-8")
    print(f"U+{cp:06X} -> {len(b)} byte(s): {b.hex(' ')}  "
          f"{' '.join(f'{x:08b}' for x in b)}")

# BOM
print("hi".encode("utf-16"))        # com BOM e ordem nativa
print("hi".encode("utf-16-le"))
print("hi".encode("utf-8-sig"))
print(b"\xef\xbb\xbfhi".decode("utf-8")[:1] == "﻿")
print(b"\xef\xbb\xbfhi".decode("utf-8-sig"))

# o mesmo texto, 4 tamanhos
text = "Programação em Python: 100% útil 😀"
for enc in ("utf-8", "utf-16", "utf-32", "latin-1"):
    try:
        print(enc, len(text.encode(enc)))
    except UnicodeEncodeError as exc:
        print(enc, "falha:", exc.reason, "em", repr(exc.object[exc.start]))
