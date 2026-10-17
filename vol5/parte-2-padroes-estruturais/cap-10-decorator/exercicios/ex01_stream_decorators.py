"""Exercício 1: o Decorator do GoF: camadas de objetos com a MESMA interface (``write``, ``flush``, ``close``) empilhadas em tempo de execução."""


class LimitExceeded(Exception):
    pass


class MemorySink:
    """O objeto de verdade (NÃO edite): guarda tudo em ``chunks`` e registra ``flushed``/``closed``."""

    def __init__(self):
        self.chunks = []
        self.flushes = 0
        self.closed = False

    def write(self, data: bytes) -> int:
        if self.closed:
            raise ValueError("sink fechado")
        self.chunks.append(data)
        return len(data)

    def flush(self) -> None:
        self.flushes += 1

    def close(self) -> None:
        self.closed = True

    def getvalue(self) -> bytes:
        return b"".join(self.chunks)


class Decorator:
    """O decorador BASE: guarda ``inner`` e delega ``write``, ``flush`` e ``close`` a ele (``write`` devolve o que o interno devolveu).
    Complete os três métodos; os decoradores abaixo herdam dele."""

    def __init__(self, inner):
        raise NotImplementedError

    def write(self, data: bytes) -> int:
        raise NotImplementedError

    def flush(self) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class CountingSink(Decorator):
    """Conta os bytes que passaram: atributo ``count`` (começa em 0) e ``writes`` (quantas chamadas a ``write``); repassa tudo ao interno."""

    def __init__(self, inner):
        raise NotImplementedError

    def write(self, data: bytes) -> int:
        raise NotImplementedError


class PrefixSink(Decorator):
    """``PrefixSink(inner, prefix)``: cada ``write(data)`` envia ``prefix + data`` ao interno; devolve ``len(data)`` (o que o CHAMADOR escreveu, sem o prefixo)."""

    def __init__(self, inner, prefix: bytes):
        raise NotImplementedError

    def write(self, data: bytes) -> int:
        raise NotImplementedError


class LimitSink(Decorator):
    """``LimitSink(inner, max_bytes)``: depois de ``max_bytes`` bytes no total, o ``write`` que ULTRAPASSARIA o limite levanta
    ``LimitExceeded(f"limite de {max_bytes} bytes")`` SEM escrever nada daquela chamada; escritas que cabem passam normalmente (o total pode ficar
    exatamente em ``max_bytes``)."""

    def __init__(self, inner, max_bytes: int):
        raise NotImplementedError

    def write(self, data: bytes) -> int:
        raise NotImplementedError


class BufferedSink(Decorator):
    """``BufferedSink(inner, size)``: junta as escritas em um buffer e só as envia ao interno (em UMA chamada a ``inner.write``) quando o buffer chega a
    ``size`` bytes ou mais (no próprio ``write`` que o completa), ou no ``flush()`` (que envia o que houver, se houver algo, e chama
    ``inner.flush()``). ``close()`` faz ``flush()`` e depois fecha o interno. ``write`` devolve ``len(data)``."""

    def __init__(self, inner, size: int):
        raise NotImplementedError

    def write(self, data: bytes) -> int:
        raise NotImplementedError

    def flush(self) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError
