"""Gabarito do exercício 2."""


class BufferPool:
    def __init__(self, buffer_size, count):
        if buffer_size < 1 or count < 1:
            raise ValueError("buffer_size e count devem ser >= 1")
        self._all = [bytearray(buffer_size) for _ in range(count)]
        self._free = list(self._all)

    def acquire(self):
        if not self._free:
            raise BufferError("sem buffers livres")
        return self._free.pop()

    def release(self, buf):
        if not any(buf is b for b in self._all) or any(buf is b for b in self._free):
            raise ValueError("buffer desconhecido")
        self._free.append(buf)

    @property
    def free(self):
        return len(self._free)


def copy_stream(src, dst, pool):
    buf = pool.acquire()
    total = 0
    try:
        while n := src.readinto(buf):
            dst.write(memoryview(buf)[:n])
            total += n
    finally:
        pool.release(buf)
    return total
