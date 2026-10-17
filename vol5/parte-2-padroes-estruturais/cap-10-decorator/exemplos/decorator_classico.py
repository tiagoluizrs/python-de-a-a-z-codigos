"""Decorator, forma clássica (GoF): embrulhar um OBJETO em outro com a MESMA interface, acrescentando comportamento, em camadas escolhidas em tempo de execução."""
import random
import time
import zlib
from abc import ABC, abstractmethod


# --- 1. a interface comum e o objeto "de verdade" ---
class DataSource(ABC):
    @abstractmethod
    def write(self, data: bytes) -> None: ...

    @abstractmethod
    def read(self) -> bytes: ...


class MemorySource(DataSource):
    def __init__(self):
        self.stored = b""

    def write(self, data):
        self.stored = data

    def read(self):
        return self.stored


# --- 2. o decorador base: tem a MESMA interface e guarda um objeto da mesma interface ---
class DataSourceDecorator(DataSource):
    def __init__(self, inner: DataSource):
        self._inner = inner

    def write(self, data):
        self._inner.write(data)

    def read(self):
        return self._inner.read()


class Compression(DataSourceDecorator):
    def write(self, data):
        super().write(zlib.compress(data))

    def read(self):
        return zlib.decompress(super().read())


class Scramble(DataSourceDecorator):
    """Uma cifra DIDÁTICA (XOR com um fluxo pseudoaleatório): serve para mostrar a ordem das camadas; NÃO é segurança de verdade."""

    def __init__(self, inner, seed=7):
        super().__init__(inner)
        self._seed = seed

    def _xor(self, data):
        stream = random.Random(self._seed).randbytes(len(data))
        return bytes(a ^ b for a, b in zip(data, stream))

    def write(self, data):
        super().write(self._xor(data))

    def read(self):
        return self._xor(super().read())


class Logging(DataSourceDecorator):
    def __init__(self, inner, name):
        super().__init__(inner)
        self._name = name

    def write(self, data):
        print(f"  [{self._name}] write {len(data)} bytes")
        super().write(data)

    def read(self):
        data = super().read()
        print(f"  [{self._name}] read {len(data)} bytes")
        return data


# --- 3. compor em tempo de execução: cada camada é um objeto, e as camadas se empilham ---
text = (b"o rato roeu a roupa do rei de Roma " * 300)
print(f"texto original: {len(text)} bytes\n")

only = MemorySource()
only.write(text)
print("sem decoradores:", len(only.stored), "bytes guardados")

pipeline = Logging(Compression(Scramble(MemorySource())), "externa")
pipeline.write(text)
print("lendo de volta:", pipeline.read() == text, "(round trip correto)")

# --- 4. a ORDEM das camadas muda o resultado: comprimir ANTES de embaralhar, não depois ---
def stored_size(builder):
    inner = MemorySource()
    outer = builder(inner)
    outer.write(text)
    assert outer.read() == text
    return len(inner.stored)


compress_then_scramble = stored_size(lambda s: Compression(Scramble(s)))        # write: comprime e DEPOIS embaralha
scramble_then_compress = stored_size(lambda s: Scramble(Compression(s)))        # write: embaralha e DEPOIS tenta comprimir
print(f"\ncomprimir e depois embaralhar: {compress_then_scramble} bytes | embaralhar e depois comprimir: {scramble_then_compress} bytes")
print("dados embaralhados parecem aleatórios e NÃO comprimem: a ordem das camadas é parte do design")

# --- 5. o custo de cada camada ---
def best(fn, n=20_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


class Null(DataSource):
    def write(self, data):
        pass

    def read(self):
        return b""


small = b"x" * 64
layers = [Null()]
for i in range(3):
    layers.append(DataSourceDecorator(layers[-1]))
print("\ncusto de uma escrita de 64 bytes, por número de camadas SEM trabalho nenhum (só a delegação):")
for n, obj in enumerate(layers):
    print(f"  {n} camadas: {best(lambda: obj.write(small)):.2f} µs")
print("cada camada acrescenta uma chamada de método (dezenas de ns); o custo real de uma camada é o TRABALHO que ela faz (comprimir, criptografar)")
