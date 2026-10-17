"""Gabarito do exercício 1."""


class LimitExceeded(Exception):
    pass


class MemorySink:
    def __init__(self):
        self.chunks = []
        self.flushes = 0
        self.closed = False

    def write(self, data):
        if self.closed:
            raise ValueError("sink fechado")
        self.chunks.append(data)
        return len(data)

    def flush(self):
        self.flushes += 1

    def close(self):
        self.closed = True

    def getvalue(self):
        return b"".join(self.chunks)


class Decorator:
    def __init__(self, inner):
        self._inner = inner

    def write(self, data):
        return self._inner.write(data)

    def flush(self):
        self._inner.flush()

    def close(self):
        self._inner.close()


class CountingSink(Decorator):
    def __init__(self, inner):
        super().__init__(inner)
        self.count = 0
        self.writes = 0

    def write(self, data):
        self.writes += 1
        self.count += len(data)
        return super().write(data)


class PrefixSink(Decorator):
    def __init__(self, inner, prefix):
        super().__init__(inner)
        self._prefix = prefix

    def write(self, data):
        super().write(self._prefix + data)
        return len(data)


class LimitSink(Decorator):
    def __init__(self, inner, max_bytes):
        super().__init__(inner)
        self._max, self._total = max_bytes, 0

    def write(self, data):
        if self._total + len(data) > self._max:
            raise LimitExceeded(f"limite de {self._max} bytes")
        self._total += len(data)
        return super().write(data)


class BufferedSink(Decorator):
    def __init__(self, inner, size):
        super().__init__(inner)
        self._size, self._buffer = size, bytearray()

    def write(self, data):
        self._buffer += data
        if len(self._buffer) >= self._size:
            self._send()
        return len(data)

    def _send(self):
        if self._buffer:
            super().write(bytes(self._buffer))
            self._buffer.clear()

    def flush(self):
        self._send()
        super().flush()

    def close(self):
        self.flush()
        super().close()
