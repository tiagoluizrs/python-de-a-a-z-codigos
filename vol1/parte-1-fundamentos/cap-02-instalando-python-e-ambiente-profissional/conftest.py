"""Fixture que carrega o exercício do aluno ou o gabarito.

Por padrão os testes importam de ``exercicios/``. Para validar os gabaritos::

    CHECK_GABARITOS=1 uv run pytest          # Linux/macOS
    $env:CHECK_GABARITOS=1; uv run pytest    # PowerShell
"""
import importlib.util
import os
from pathlib import Path

import pytest

CHAPTER_DIR = Path(__file__).parent


@pytest.fixture
def load_exercise():
    folder = "gabaritos" if os.environ.get("CHECK_GABARITOS") else "exercicios"

    def _load(name: str):
        path = CHAPTER_DIR / folder / f"{name}.py"
        spec = importlib.util.spec_from_file_location(f"{folder}_{name}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    return _load
