"""O str ocupa 1, 2 ou 4 bytes por caractere, conforme o maior caractere (PEP 393)."""
import sys

# Textos montados em tempo de execução, para evitar strings únicas já em cache
samples = {
    "ASCII":       "a" * 10,
    "Latin-1":     "é" * 10,
    "BMP (UCS-2)": "你" * 10,
    "Astral (UCS-4)": "😀" * 10,
}
for name, text in samples.items():
    print(f"{name:<16} len={len(text)}  getsizeof={sys.getsizeof(text)}  max code point={max(map(ord, text)):#x}")

# Um único caractere "largo" muda a representação do texto INTEIRO
print(sys.getsizeof("a" * 1000))
print(sys.getsizeof("a" * 999 + "😀"))
