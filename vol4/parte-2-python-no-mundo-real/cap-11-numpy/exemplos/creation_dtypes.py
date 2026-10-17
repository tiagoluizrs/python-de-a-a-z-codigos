"""Criação de arrays e a escolha do dtype (inclusive os estouros silenciosos)."""
import warnings

import numpy as np

# 1. as formas de criar
print("array de lista   :", np.array([1, 2, 3]))
print("zeros / ones     :", np.zeros(3), np.ones((2, 2), dtype=np.int8).tolist())
print("full             :", np.full(3, 7.5))
print("arange (passo)   :", np.arange(0, 10, 3))
print("linspace (n pts) :", np.linspace(0, 1, 5))
print("eye              :", np.eye(3, dtype=int).tolist())
print("fromiter         :", np.fromiter((x * x for x in range(5)), dtype=np.int64))
print("empty não zera   : conteúdo = lixo da memória (use só se vai preencher tudo)")

# 2. dtype inferido
print("\ninferência:", np.array([1, 2]).dtype, np.array([1, 2.0]).dtype, np.array([1, "a"]).dtype,
      np.array([1, None]).dtype, np.array([True, 2]).dtype)

# 3. o estouro de inteiros é SILENCIOSO (aritmética de tamanho fixo, ao contrário do int do Python)
small = np.array([100, 120], dtype=np.int8)
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    scalar = small[0] + small[0]               # escalar NumPy: avisa (RuntimeWarning)
    whole = small + small                      # array inteiro: NÃO avisa
print("\nint8: 100 + 100 =", scalar, "(deveria ser 200) | avisos nos escalares:", len(caught))
print("int8: array + array =", whole, "| nenhum aviso: o estouro é silencioso")
print("Python: 100 + 100 =", 100 + 100, "| 2**100 =", 2**100)
big = np.array([2**62], dtype=np.int64)
print("int64: 2**62 * 4 =", big * 4, "(dá a volta)")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    print("uint8: 3 - 5 =", np.uint8(3) - np.uint8(5), "(dá a volta em 256)")

# 4. promoção de tipos nas operações
print("\nint8 + int8   :", (np.int8(1) + np.int8(1)).dtype)
print("int8 + int16  :", (np.int8(1) + np.int16(1)).dtype)
print("int64 + float32:", (np.int64(1) + np.float32(1)).dtype, "(sobe para float64)")
print("array int8 + escalar Python 1000:", end=" ")
try:
    print((np.array([1], dtype=np.int8) + 1000).dtype)
except OverflowError as error:
    print("OverflowError:", str(error)[:60])

# 5. float: precisão e o preço dela
x64 = np.float64(0.1) + np.float64(0.2)
x32 = np.float32(0.1) + np.float32(0.2)
print("\nfloat64 0.1+0.2 =", repr(x64), "| float32 0.1+0.2 =", repr(x32))
print("eps float64:", np.finfo(np.float64).eps, "| eps float32:", np.finfo(np.float32).eps)
print("float32 acumulado: 1e8 + 1 =", np.float32(1e8) + np.float32(1), "(o +1 sumiu)")
print("limites: int8", np.iinfo(np.int8).min, np.iinfo(np.int8).max, "| uint8", np.iinfo(np.uint8).max,
      "| int64", np.iinfo(np.int64).max)

# 6. astype copia; casts que perdem dados não avisam
f = np.array([1.9, -1.9, 300.7, np.nan])
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    print("\nfloat -> int8 :", f.astype(np.int8), "(trunca, estoura e NaN vira lixo)")
print("float -> int64 trunca para zero:", np.array([1.9, -1.9]).astype(np.int64), "| round antes:",
      np.round([1.9, -1.9]).astype(np.int64))

# 7. tipos de data, texto e estruturados
days = np.array(["2026-01-01", "2026-03-01"], dtype="datetime64[D]")
print("\ndatetime64:", days, "| diferença:", days[1] - days[0])
people = np.array([("Ana", 30, 1.62), ("Bia", 25, 1.70)], dtype=[("name", "U10"), ("age", "i4"), ("h", "f8")])
print("estruturado:", people["name"], people["age"].mean(), "| itemsize:", people.dtype.itemsize, "bytes/linha")
print("object (evite):", np.array([1, "a", None], dtype=object).dtype, "- volta a ser lista de ponteiros, sem ganho")

# 8. escolher dtype é decisão de memória: pixels, coordenadas, flags
for name, dt in [("uint8 (pixel)", np.uint8), ("float32 (GPU/ML)", np.float32), ("float64 (padrão)", np.float64),
                 ("bool (máscara)", np.bool_)]:
    print(f"  1 milhão de {name:<18} = {np.zeros(1_000_000, dtype=dt).nbytes / 1e6:5.1f} MB")
