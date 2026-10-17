"""Exercício 2: um deepcopy simplificado com memo."""


def my_deepcopy(obj, memo: dict | None = None):
    """Copie ``obj`` recursivamente, sem usar o módulo ``copy``.

    Requisitos:
    - atômicos (int, float, str, bytes, bool, None) são devolvidos como estão;
    - suporte a list, dict, set e tuple;
    - o ``memo`` mapeia ``id(original) -> cópia``: objetos compartilhados no
      original continuam compartilhados na cópia;
    - ciclos funcionam: registre a cópia vazia no memo ANTES de preenchê-la
      (para tuplas, que são imutáveis, copie os itens e depois registre);
    - uma tupla cujos itens copiados são todos os mesmos objetos
      pode devolver a própria tupla.

    >>> a = [1]; a.append(a); b = my_deepcopy(a); b[1] is b
    True
    """
    raise NotImplementedError
