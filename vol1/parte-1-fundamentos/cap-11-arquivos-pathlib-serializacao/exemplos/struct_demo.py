"""struct: empacotar e desempacotar binário com layout fixo."""
import struct

# cabeçalho fictício: magic (4 bytes), versão (u16), flags (u16),
# tamanho (u32), todos em little-endian ("<")
HEADER = struct.Struct("<4sHHI")
print(HEADER.size, "bytes")

packed = HEADER.pack(b"DEMO", 1, 0b101, 1024)
print(packed)
print(packed.hex(" "))

magic, version, flags, size = HEADER.unpack(packed)
print(magic, version, flags, size)

# ordem dos bytes importa
print(struct.pack("<I", 1), struct.pack(">I", 1))

# sem prefixo, struct usa alinhamento nativo (padding!)
print(struct.calcsize("BI"), struct.calcsize("<BI"), struct.calcsize("=BI"))

# erros
try:
    struct.pack("<H", 70000)
except struct.error as exc:
    print("struct.error:", exc)
try:
    HEADER.unpack(packed[:5])
except struct.error as exc:
    print("struct.error:", exc)

# lendo registros de tamanho fixo de um buffer
records = b"".join(struct.pack("<If", i, i * 1.5) for i in range(3))
print(list(struct.iter_unpack("<If", records)))

# int.to_bytes / from_bytes cobrem o caso de um único inteiro
print((1024).to_bytes(4, "little"), int.from_bytes(b"\x00\x04", "big"))
