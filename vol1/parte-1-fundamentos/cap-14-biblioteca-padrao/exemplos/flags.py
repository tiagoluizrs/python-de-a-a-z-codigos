"""enum.Flag e enum.IntFlag: permissões combináveis."""
from enum import Flag, IntFlag, auto


class Perm(Flag):
    NONE = 0
    READ = auto()
    WRITE = auto()
    EXEC = auto()
    RW = READ | WRITE          # alias composto
    ALL = READ | WRITE | EXEC


mode = Perm.READ | Perm.WRITE
print(mode)
print(Perm.READ in mode, Perm.EXEC in mode)
print(mode & ~Perm.WRITE)         # remove WRITE
print(Perm.ALL ^ Perm.EXEC)       # alterna EXEC
print(list(Perm.ALL))             # decompõe em flags simples
print(mode.value, bool(Perm.NONE))
print(Perm(3), Perm(0))


class UnixPerm(IntFlag):
    X = 1
    W = 2
    R = 4


p = UnixPerm.R | UnixPerm.W
print(p, int(p), p == 6, oct(p | UnixPerm.X))
print(UnixPerm(5))

try:
    Perm.READ + Perm.WRITE         # Flag não é número
except TypeError as exc:
    print("TypeError:", exc)

try:
    Perm(16)
except ValueError as exc:
    print("ValueError:", exc)
