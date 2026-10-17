"""Exercício 4: ordenar imports como o isort/ruff."""


def sort_imports(source):
    """``source`` contém SÓ linhas de import (``import x``, ``import a, b``,
    ``from x import y, z``, com ``as``) e linhas em branco. Devolve o texto
    reorganizado, terminado em ``"\\n"``:

    * ``import a, b`` vira duas linhas;
    * seções, nesta ordem, separadas por UMA linha em branco: ``__future__``,
      biblioteca padrão (``sys.stdlib_module_names``, pelo primeiro
      componente), terceiros, locais (``from .x import y``);
    * dentro de uma seção: primeiro os ``import x``, depois os
      ``from x import y``; cada grupo em ordem alfabética sem diferenciar
      maiúsculas pelo nome do módulo;
    * nomes dentro de ``from m import b, a`` ficam ordenados (sem diferenciar
      maiúsculas): ``from m import a, b``;
    * ``as`` é preservado.
    Sem imports, devolve ``""``."""
    raise NotImplementedError
