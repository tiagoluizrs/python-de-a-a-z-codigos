"""Epoch, o ano 2038 e como o int ilimitado do Python escapa."""
import ctypes
import datetime as dt
import struct
import time

print("epoch agora (s) :", int(time.time()))
print("epoch agora (ns):", time.time_ns())
print(dt.datetime.fromtimestamp(0, dt.UTC))

limit = 2**31 - 1   # maior inteiro de 32 bits com sinal
print("limite 32 bits  :", dt.datetime.fromtimestamp(limit, dt.UTC))
print("um segundo depois:",
      dt.datetime.fromtimestamp(limit + 1, dt.UTC))

# O que acontece em C: o valor "dá a volta" (wraparound).
wrapped = ctypes.c_int32(limit + 1).value
print("int32 após estouro:", wrapped)
print("vira a data     :", dt.datetime.fromtimestamp(wrapped, dt.UTC))

try:
    struct.pack("<i", limit + 1)   # gravar em 4 bytes com sinal
except struct.error as error:
    print("struct:", error)
print("em 8 bytes cabe :", struct.pack("<q", limit + 1).hex())

# O int do Python não estoura. Quem limita é o datetime (ano 9999)
# e, às vezes, a plataforma (ver abaixo).
epoch = dt.datetime(1970, 1, 1, tzinfo=dt.UTC)
for seconds in (2**31, 2**35, 253_402_300_799):
    print(seconds, "->", epoch + dt.timedelta(seconds=seconds))

for seconds in (2**35, 2**40):
    try:
        print(dt.datetime.fromtimestamp(seconds, dt.UTC))
    except (OSError, OverflowError, ValueError) as error:
        print(f"fromtimestamp({seconds}):", type(error).__name__, error)
