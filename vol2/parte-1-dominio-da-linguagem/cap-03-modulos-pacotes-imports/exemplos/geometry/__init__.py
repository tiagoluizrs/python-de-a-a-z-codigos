"""Pacote de exemplo: a API pública é reexportada aqui."""
from .shapes import Circle, Rectangle
from .utils.maths import clamp

__all__ = ["Circle", "Rectangle", "clamp", "__version__"]
__version__ = "1.0"
print(f"[geometry] __init__ executado (__name__={__name__!r})")
