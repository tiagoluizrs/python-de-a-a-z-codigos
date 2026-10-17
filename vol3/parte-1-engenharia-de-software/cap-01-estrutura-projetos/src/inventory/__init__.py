"""inventory: um pequeno controle de estoque, para ilustrar a estrutura de um projeto."""
from importlib.metadata import PackageNotFoundError, version

from .core import Inventory, Item, OutOfStockError

try:
    __version__ = version("cap-01-estrutura-projetos")      # única fonte da verdade: o pyproject.toml
except PackageNotFoundError:                                # rodando sem instalar
    __version__ = "0+unknown"

__all__ = ["Inventory", "Item", "OutOfStockError", "__version__"]
