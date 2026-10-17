"""Anatomia de um ndarray: buffer, dtype, shape, strides, views e cópias."""
import array
import sys

import numpy as np

print("numpy", np.__version__)

# 1. lista de objetos x bloco compacto de números
n = 1_000_000
as_list = list(range(n))
as_array = np.arange(n, dtype=np.int64)
list_bytes = sys.getsizeof(as_list) + sum(sys.getsizeof(x) for x in as_list)
print(f"\nlist de {n:,} int : {list_bytes / 1e6:6.1f} MB  (ponteiros + um objeto int por item)")
print(f"ndarray int64     : {as_array.nbytes / 1e6:6.1f} MB  (um bloco, 8 bytes por item)")
print(f"ndarray int32     : {as_array.astype(np.int32).nbytes / 1e6:6.1f} MB")
print(f"ndarray int8      : {as_array.astype(np.int8).nbytes / 1e6:6.1f} MB (e estoura: ver creation_dtypes.py)")

# 2. os cinco atributos que descrevem o array
a = np.arange(12, dtype=np.int32).reshape(3, 4)
print("\na =\n", a)
print("dtype:", a.dtype, "| itemsize:", a.itemsize, "| shape:", a.shape, "| ndim:", a.ndim, "| size:", a.size)
print("strides (bytes para andar 1 passo em cada eixo):", a.strides)
print("nbytes:", a.nbytes, "| flags C/F contíguo:", a.flags["C_CONTIGUOUS"], a.flags["F_CONTIGUOUS"])

# 3. transpor NÃO copia nada: troca os strides
t = a.T
print("\na.T.strides:", t.strides, "| compartilha memória com a?", np.shares_memory(a, t))
print("a.T contíguo em C?", t.flags["C_CONTIGUOUS"], "(o mesmo bloco, lido em outra ordem)")

# 4. view x cópia
view = a[:, 1:3]                       # fatia básica: VIEW (mesmo bloco)
copy = a[:, [1, 2]]                    # índice por lista: CÓPIA
view[0, 0] = 99
print("\napós view[0,0] = 99, a[0,1] =", a[0, 1], "| view compartilha memória?", np.shares_memory(a, view))
print("a cópia compartilha memória?", np.shares_memory(a, copy), "| copy[0,0] =", copy[0, 0])
print("a[:, 1:3].strides:", view.strides, "(pula elementos sem copiar)")

# 5. reshape devolve view quando dá; ravel também; flatten SEMPRE copia
b = np.arange(6)
print("\nreshape é view?", np.shares_memory(b, b.reshape(2, 3)),
      "| ravel é view?", np.shares_memory(b, b.ravel()),
      "| flatten é view?", np.shares_memory(b, b.flatten()))
print("transposta .ravel() precisa copiar?", not np.shares_memory(a, a.T.ravel()))

# 6. o buffer protocol: array.array, bytes, memoryview e ndarray enxergam a MESMA memória
raw = array.array("d", [1.0, 2.0, 3.0])
shared = np.frombuffer(raw, dtype=np.float64)
raw[0] = 100.0
print("\nndarray sobre array.array:", shared, "| memória compartilhada (sem cópia):", shared.base is not None)
ro = np.frombuffer(b"\x01\x02\x03\x04", dtype=np.uint8)
print("frombuffer sobre bytes é somente leitura?", not ro.flags.writeable)

# 7. o custo de cada elemento visto de fora
x = as_array[10]
print("\nas_array[10] devolve", type(x).__name__, "(escalar NumPy), não int; .item() dá", type(x.item()).__name__)
