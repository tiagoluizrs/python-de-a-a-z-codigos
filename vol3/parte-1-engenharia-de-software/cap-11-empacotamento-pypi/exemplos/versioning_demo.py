"""Versões de lançamento: ordem, pré-lançamentos, correções e versões locais."""
from packaging.version import Version

releases = ["1.0.dev1", "1.0a1", "1.0b2", "1.0rc1", "1.0", "1.0.post1", "1.0.1", "1.1", "2.0.dev0", "2.0"]
assert sorted(releases, key=Version) == releases
print("ordem correta:", " < ".join(releases))

v = Version("1.4.2")
print("partes:", v.major, v.minor, v.micro, "| pré-lançamento?", Version("1.5.0rc1").is_prerelease, "| dev?", Version("1.5.0.dev3").is_devrelease)
print("local (não vai para o PyPI):", Version("1.4.2+ubuntu.1"), Version("1.4.2+ubuntu.1") > Version("1.4.2"))
print("normalização:", Version("1.0.0") == Version("1"), Version("1.4.2-rc.1"), Version("v2.0"))

# O que um instalador escolhe: pré-lançamentos só se pedidos
from packaging.specifiers import SpecifierSet

available = [Version(x) for x in ["1.4.2", "1.5.0rc1", "1.5.0", "1.6.0.dev1"]]
spec = SpecifierSet(">=1.4")
print("sem --pre:", max(spec.filter(available)), "| com --pre:", max(spec.filter(available, prereleases=True)))

# PyPI: uma versão publicada NUNCA pode ser substituída ou reutilizada (só "yanked")
print("fluxo seguro: 1.5.0rc1 (TestPyPI) -> 1.5.0rc2 -> 1.5.0 (PyPI)")
