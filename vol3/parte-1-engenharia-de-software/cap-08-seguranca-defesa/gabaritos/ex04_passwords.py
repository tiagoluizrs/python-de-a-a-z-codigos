"""Gabarito do exercício 4."""
import hashlib
import hmac
import secrets


def _derive(password, salt, n, r, p):
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=32, maxmem=256 * 1024 * 1024)


def hash_password(password, *, n=2**14, r=8, p=1):
    salt = secrets.token_bytes(16)
    return f"scrypt${n}${r}${p}${salt.hex()}${_derive(password, salt, n, r, p).hex()}"


def _parse(stored):
    parts = stored.split("$")
    if len(parts) != 6 or parts[0] != "scrypt":
        raise ValueError
    n, r, p = (int(x) for x in parts[1:4])
    return n, r, p, bytes.fromhex(parts[4]), bytes.fromhex(parts[5])


def verify_password(password, stored):
    try:
        n, r, p, salt, expected = _parse(stored)
        actual = _derive(password, salt, n, r, p)
    except (ValueError, TypeError, AttributeError, OverflowError, MemoryError):
        return False
    return hmac.compare_digest(actual, expected)


def needs_rehash(stored, *, n=2**14, r=8, p=1):
    try:
        sn, sr, sp, _, _ = _parse(stored)
    except (ValueError, TypeError, AttributeError):
        return True
    return sn < n or sr < r or sp < p
