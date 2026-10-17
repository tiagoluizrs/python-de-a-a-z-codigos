"""Especificadores de versão, requisitos e marcadores de ambiente."""
from packaging.markers import Marker
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

spec = SpecifierSet(">=2.0,<3")
print(spec, [str(Version(v) in spec) for v in ("1.9", "2.0", "2.7.3", "3.0")])

# ~= (compatível): ~=2.2 significa >=2.2,<3 ; ~=2.2.1 significa >=2.2.1,<2.3
for text, versions in [("~=2.2", ["2.1", "2.2", "2.9", "3.0"]), ("~=2.2.1", ["2.2.0", "2.2.1", "2.2.9", "2.3.0"])]:
    s = SpecifierSet(text)
    print(f"{text:<8}", {v: v in s for v in versions})

# == com curinga e !=
print("2.5" in SpecifierSet("==2.*"), "3.0" in SpecifierSet("==2.*"), "2.5" in SpecifierSet(">=2,!=2.5"))

# Pré-lançamentos só são escolhidos (filter) se pedidos explicitamente
candidates = ["1.0", "2.1rc1", "2.0"]
print(list(SpecifierSet(">=2.0").filter(candidates)),
      list(SpecifierSet(">=2.0").filter(candidates, prereleases=True)),
      list(SpecifierSet(">=2.1rc1").filter(["2.1rc1"])))

# Requisitos completos: nome, extras, especificador, marcador
req = Requirement("requests[socks,security]>=2.31,<3 ; python_version >= '3.10' and sys_platform != 'emscripten'")
print(req.name, sorted(req.extras), str(req.specifier), req.marker)
print(Requirement("Django_REST.framework>=3").name)             # o nome é preservado; a comparação normaliza

# Marcadores: condições sobre o AMBIENTE
marker = Marker("sys_platform == 'win32' and python_version >= '3.15'")
print(marker.evaluate(), marker.evaluate({"sys_platform": "linux"}))

# Requisitos inválidos
for bad in ("requests>=", "requests[", "==1.0"):
    try:
        Requirement(bad)
    except InvalidRequirement as error:
        print("InvalidRequirement:", str(error).splitlines()[0][:50])
