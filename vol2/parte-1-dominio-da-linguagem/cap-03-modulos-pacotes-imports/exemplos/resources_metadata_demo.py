"""importlib.resources (dados dentro de pacotes) e importlib.metadata."""
from importlib import metadata, resources

import geometry

# 1. Arquivo de dados que mora dentro do pacote
data = resources.files("geometry") / "data" / "units.json"
print(data.name, data.is_file(), data.read_text("utf-8").strip())

# Para um programa externo que precisa de um caminho real:
with resources.as_file(data) as real_path:
    print(real_path.name, real_path.exists())

# Listar o conteudo de um pacote
print(sorted(p.name for p in resources.files("geometry").iterdir()
             if not p.name.startswith("__")))

# 2. Metadados de pacotes INSTALADOS (nao de modulos soltos)
print(metadata.version("pytest")[:1].isdigit())
meta = metadata.metadata("pytest")
print(meta["Name"], "|", meta["Requires-Python"])
try:
    metadata.version("geometry")      # pasta solta nao e distribuicao
except metadata.PackageNotFoundError as exc:
    print("PackageNotFoundError:", exc)
print([e.name for e in metadata.entry_points(group="console_scripts")
       if e.name.startswith("py.test")])
