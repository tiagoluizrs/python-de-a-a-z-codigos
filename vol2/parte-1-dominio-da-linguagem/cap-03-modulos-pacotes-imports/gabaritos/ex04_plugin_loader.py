"""Gabarito do exercicio 4: carregador de plugins."""
import importlib.util
from collections.abc import Callable
from pathlib import Path


def load_plugins(folder: Path) -> dict[str, Callable]:
    plugins: dict[str, Callable] = {}
    for path in sorted(folder.glob("*.py")):
        if path.name.startswith("_"):
            continue
        # Carrega pelo caminho, sem alterar sys.path
        spec = importlib.util.spec_from_file_location(
            f"plugin_{path.stem}", path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            info = module.register()
        except Exception:        # plugin quebrado nao derruba os outros
            continue
        plugins[info["name"]] = info["run"]
    return plugins
