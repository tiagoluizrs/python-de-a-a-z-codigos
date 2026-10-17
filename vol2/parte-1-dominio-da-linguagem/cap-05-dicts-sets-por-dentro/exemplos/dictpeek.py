"""Espia a tabela interna de um dict e de um set com ctypes.

ATENCAO: o layout interno NAO e API. Os offsets abaixo valem para o
CPython 3.15.0 (build padrao, com GIL, 64 bits) e foram conferidos
contra sys.getsizeof. Em outra versao ou build, o resultado e lixo
(ou um travamento). Use somente para estudar, nunca em producao.
"""
import ctypes
import sys

assert sys.maxsize > 2**32, "layout de 64 bits"

_U8, _U64 = ctypes.c_uint8, ctypes.c_uint64
_INT = {1: ctypes.c_int8, 2: ctypes.c_int16,
        4: ctypes.c_int32, 8: ctypes.c_int64}


def _read(addr, ctype=_U64):
    return ctype.from_address(addr).value


def _obj(ptr):
    return ctypes.cast(ptr, ctypes.py_object).value


def inspect_dict(d):
    """Devolve a anatomia da tabela de um dict (indices + entradas)."""
    keys = _read(id(d) + 32)               # ma_keys
    log2_size = _read(keys + 8, _U8)
    log2_index_bytes = _read(keys + 9, _U8)
    kind = _read(keys + 10, _U8)
    usable = _read(keys + 16, ctypes.c_int64)
    nentries = _read(keys + 24, ctypes.c_int64)
    slots = 1 << log2_size
    index_bytes = 1 << log2_index_bytes
    width = index_bytes // slots
    indices = [_read(keys + 32 + i * width, _INT[width])
               for i in range(slots)]
    entries_at = keys + 32 + index_bytes
    # Com chaves apenas str o CPython guarda (chave, valor): 16 bytes.
    entry_size = 16 if kind else 24
    entries = []
    for i in range(nentries):
        base = entries_at + i * entry_size
        if kind:
            hash_, key_p, val_p = None, _read(base), _read(base + 8)
        else:
            hash_ = _read(base, ctypes.c_int64)
            key_p, val_p = _read(base + 8), _read(base + 16)
        key = _obj(key_p) if key_p else None   # None = entrada apagada
        entries.append((hash_, key, bool(val_p)))
    return {"slots": slots, "index_width": width, "kind": kind,
            "entry_size": entry_size, "usable": usable,
            "nentries": nentries, "indices": indices,
            "entries": entries}


def model_getsizeof(slots, usable, entry_size, index_width):
    """Modelo que reproduz sys.getsizeof(dict): 64 + 32 + tabelas."""
    return 64 + 32 + slots * index_width + usable * entry_size


def dict_capacity(d):
    """(slots, capacidade de entradas) lidos da tabela real."""
    info = inspect_dict(d)
    return info["slots"], info["usable"] + info["nentries"]
