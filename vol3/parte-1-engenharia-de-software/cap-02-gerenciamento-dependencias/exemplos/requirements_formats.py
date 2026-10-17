"""Os formatos de declarar dependências, e como lê-los."""
from packaging.requirements import Requirement

TEXT = """\
# dependências de produção
requests==2.34.2        # versão exata
flask>=3,<4
numpy ; python_version >= "3.12"
rich[jupyter]~=15.0
-r outro.txt
-e ./libs/local
"""

for line in TEXT.splitlines():
    clean = line.split(" #")[0].strip()
    if not clean or clean.startswith("#"):
        continue
    if clean.startswith("-"):
        print(f"opção do pip (não é requisito): {clean}")
        continue
    req = Requirement(clean)
    print(f"{req.name:<10} especificador={str(req.specifier) or '(qualquer)':<12} extras={sorted(req.extras)} marcador={req.marker}")
