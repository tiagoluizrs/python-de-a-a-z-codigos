"""Exercício 6: formatador de moeda pt-BR sem depender do locale."""
from decimal import Decimal


def format_brl(value: int | float | str | Decimal, symbol: bool = True) -> str:
    """Formate ``value`` como moeda brasileira.

        format_brl(1234567.891) == "R$ 1.234.567,89"
        format_brl("1999.9", symbol=False) == "1.999,90"
        format_brl(0) == "R$ 0,00"
        format_brl(-0.5) == "-R$ 0,50"
        format_brl(Decimal("2.675")) == "R$ 2,68"   # meio para cima

    Regras:
    - duas casas decimais, arredondando metade para cima (ROUND_HALF_UP);
    - separador de milhar ``.`` e decimal ``,``;
    - sinal negativo antes do símbolo;
    - converta floats via ``Decimal(str(value))`` para evitar surpresas
      binárias (``2.675`` vira exatamente 2.675).
    - um valor que arredonda para zero NÃO leva sinal: ``-0.001`` -> ``"R$ 0,00"``.
    """
    raise NotImplementedError
