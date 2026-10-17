"""Exercício 6: o autofix de imports não usados."""


def remove_unused_imports(source):
    """Remove os imports não usados de ``source`` (texto) e devolve o novo texto.

    * considere só instruções ``import``/``from ... import`` de UMA linha, no
      nível do módulo; instruções em várias linhas ficam intactas;
    * um nome é usado se aparece como ``ast.Name`` ou em ``__all__``;
    * ``from __future__ import ...`` e ``import *`` nunca são tocados;
    * se TODOS os nomes de uma linha são inúteis, a linha some; se só alguns,
      a linha é reescrita só com os usados (``import a, c``;
      ``from m import x, z as w``), mantendo o recuo e a ordem original;
    * o resto do texto fica idêntico (inclusive a quebra de linha final)."""
    raise NotImplementedError
