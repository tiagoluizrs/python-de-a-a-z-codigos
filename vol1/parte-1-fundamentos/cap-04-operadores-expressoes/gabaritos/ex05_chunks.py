"""Gabarito do exercício 5."""
import io


def read_in_chunks(stream: io.BufferedIOBase, size: int) -> list[bytes]:
    chunks = []
    while chunk := stream.read(size):    # b"" é falso: encerra o laço no fim
        chunks.append(chunk)
    return chunks
