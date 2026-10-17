"""Gabarito 2: ler em blocos com gerador."""


def read_in_chunks(stream, size=4096):
    if size < 1:
        raise ValueError("size must be >= 1")  # só ao consumir
    # read() devolve vazio no fim; vazio é falso, então o laço para
    while chunk := stream.read(size):
        yield chunk


def count_bytes(stream, size=4096):
    return sum(len(chunk) for chunk in read_in_chunks(stream, size))
