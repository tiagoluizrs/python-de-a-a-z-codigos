"""Exercício 2: abrindo um float (IEEE 754, 64 bits)."""


def float_bits(value: float) -> tuple[int, int, int]:
    """Devolva ``(sinal, expoente, mantissa)`` do float.

    sinal: 1 bit; expoente: 11 bits (sem remover o viés de 1023);
    mantissa: 52 bits. Exemplo: ``float_bits(-2.0) == (1, 1024, 0)``.
    Dica: ``struct.pack('>d', value)`` e ``int.from_bytes``.
    """
    raise NotImplementedError
