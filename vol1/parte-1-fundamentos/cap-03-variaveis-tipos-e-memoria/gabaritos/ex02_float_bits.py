"""Gabarito do exercício 2."""
import struct


def float_bits(value: float) -> tuple[int, int, int]:
    bits = int.from_bytes(struct.pack(">d", value), "big")
    sign = bits >> 63
    exponent = (bits >> 52) & 0x7FF      # 11 bits
    mantissa = bits & ((1 << 52) - 1)    # 52 bits
    return sign, exponent, mantissa
