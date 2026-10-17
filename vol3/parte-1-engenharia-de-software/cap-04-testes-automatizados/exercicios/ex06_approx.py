"""Exercício 6: comparação aproximada, como ``pytest.approx``."""
import math


def approx_equal(actual, expected, rel=1e-6, abs_tol=1e-12, nan_ok=False):
    """``True`` se ``actual`` é aproximadamente igual a ``expected``.

    * números (``int``/``float``): ``abs(a - e) <= max(rel * abs(e), abs_tol)``;
      iguais (inclusive ``inf == inf``) são ``True``; ``nan`` só é igual a
      ``nan`` se ``nan_ok``;
    * ``list``/``tuple``: mesmo tamanho e elemento a elemento (recursivo);
    * ``dict``: mesmas chaves e valores aproximados (recursivo);
    * qualquer outro tipo: ``==``;
    * tipos incompatíveis (número x lista) são ``False``;
    * ``bool`` não é número aqui: ``True`` só é igual a ``True``.
    """
    raise NotImplementedError
