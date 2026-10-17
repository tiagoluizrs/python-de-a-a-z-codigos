"""Exercício 1: uma dataclass com validação e campos derivados."""
from decimal import Decimal


class Product:
    """Transforme em ``@dataclass`` (você decide os parâmetros do decorador).

    Campos, nesta ordem:

    * ``sku: str``: normalizado para MAIÚSCULAS e sem espaços nas pontas;
    * ``name: str``: não pode ser vazio (``ValueError``);
    * ``price: Decimal``: não pode ser negativo (``ValueError``);
    * ``tags: list[str]``: padrão lista VAZIA própria de cada instância;
    * ``slug: str``: NÃO entra no ``__init__`` nem no ``repr``; derivado do
      nome (minúsculas, espaços trocados por ``-``).

    Use ``__post_init__`` para normalizar, validar e calcular o ``slug``.
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError
