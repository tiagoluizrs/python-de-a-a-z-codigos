"""Exercício 2: dividindo uma conta sem perder centavos."""
from decimal import Decimal


def split_bill(total: Decimal, people: int) -> list[Decimal]:
    """Divida ``total`` entre ``people`` pessoas, em valores de 2 casas decimais,
    de modo que a SOMA das partes seja exatamente ``total``.

    Os centavos que sobrarem são distribuídos, 1 por pessoa, começando
    pela primeira. Exemplo: ``split_bill(Decimal('100.00'), 3)``
    -> [Decimal('33.34'), Decimal('33.33'), Decimal('33.33')]
    Dica: trabalhe em centavos inteiros e use ``divmod``.
    """
    raise NotImplementedError
