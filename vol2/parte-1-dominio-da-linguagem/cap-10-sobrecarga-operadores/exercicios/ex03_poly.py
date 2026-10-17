"""Exercício 3: polinômios com operadores."""


class Poly:
    """Polinômio de coeficientes inteiros, do termo constante para cima.

    ``Poly([1, 2, 3])`` representa ``1 + 2x + 3x**2``.

    * normalize: remova zeros finais (``Poly([1, 0])`` == ``Poly([1])``);
      o polinômio nulo é ``Poly([])`` (``bool`` falso, ``degree`` igual a -1);
    * ``p + q``, ``p - q``, ``p * q`` (polinômios) e com inteiros
      (``p + 1``, ``2 * p``, ``1 + p``);
    * ``-p`` e ``p ** n`` (``n`` inteiro >= 0);
    * ``p(x)`` avalia o polinômio em ``x`` (``__call__``, use Horner);
    * ``degree`` (propriedade) e ``==`` por coeficientes;
    * ``repr`` no formato ``Poly([1, 2, 3])``.
    """

    def __init__(self, coefficients):
        raise NotImplementedError
