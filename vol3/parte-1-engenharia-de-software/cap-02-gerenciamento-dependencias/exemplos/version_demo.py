"""Versões segundo a PEP 440 (biblioteca packaging)."""
from packaging.version import InvalidVersion, Version

# Texto engana: a ordem correta é numérica por componente
print("1.10" > "1.9", Version("1.10") > Version("1.9"))
print(sorted(["1.10", "1.9", "1.2", "1.2.1"], key=Version))

# Pré-lançamentos, pós-lançamentos e desenvolvimento
order = ["1.0.dev0", "1.0a1", "1.0b2", "1.0rc1", "1.0", "1.0.post1", "1.1.dev0"]
print(sorted(order, key=Version) == order)

v = Version("2.4.1rc2")
print(v.release, v.major, v.minor, v.micro, v.pre, v.is_prerelease, v.base_version)

# Normalização: formas equivalentes são iguais
print(Version("1.0") == Version("1.0.0"), Version("1.0-1") == Version("1.0.post1"), Version("V1.0A1"))

# Epoch: o desempate de último recurso
print(Version("1!1.0") > Version("2025.1"))

# Inválidas
for text in ("1.0.foo", "abc", ""):
    try:
        Version(text)
    except InvalidVersion as error:
        print("InvalidVersion:", error)

# Calendário e SemVer coexistem no PyPI: a ordem é a mesma regra
print(Version("2026.10") > Version("2026.9"), Version("3.15.0") > Version("3.9.18"))
