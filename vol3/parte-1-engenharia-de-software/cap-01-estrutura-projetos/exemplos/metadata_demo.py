"""Metadados do pacote instalado: versão, ponto de entrada, arquivos."""
import inventory
from importlib import metadata

dist = metadata.distribution("cap-01-estrutura-projetos")
print(dist.metadata["Name"], dist.version, inventory.__version__)
print("requires-python:", dist.metadata["Requires-Python"])

scripts = [ep for ep in metadata.entry_points(group="console_scripts") if ep.dist.name == dist.name]
for entry in scripts:
    print("script:", entry.name, "->", entry.value)
    func = entry.load()                              # importa e devolve a função
    print("carregada:", func.__module__, func.__name__)

# Onde está o código? (modo editável: aponta para src/)
print("módulo carregado de:", inventory.__file__.replace("\\", "/").split("/src/")[-1])
