"""Gabarito do exercício 4."""
import importlib.util
import marshal
import os
import struct


def read_pyc_header(path):
    with open(path, "rb") as handle:
        header = handle.read(16)
    magic = header[:4]
    if magic != importlib.util.MAGIC_NUMBER:
        raise ValueError("magic number diferente do interpretador atual")
    flags, mtime, size = struct.unpack("<III", header[4:16])
    return {"magic": magic, "flags": flags, "mtime": mtime, "size": size}


def load_pyc(path):
    with open(path, "rb") as handle:
        data = handle.read()
    return marshal.loads(data[16:])


def is_fresh(source_path, pyc_path):
    header = read_pyc_header(pyc_path)
    if header["flags"] != 0:
        return False
    stat = os.stat(source_path)
    return header["mtime"] == int(stat.st_mtime) and header["size"] == stat.st_size
