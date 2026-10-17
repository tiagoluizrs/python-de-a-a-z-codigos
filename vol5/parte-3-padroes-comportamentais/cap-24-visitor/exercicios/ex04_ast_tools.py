"""Exercício 4: o Visitor da biblioteca padrão: ``ast.NodeVisitor`` (só olhar) e ``ast.NodeTransformer`` (reescrever) sobre código Python de verdade."""
import ast


def function_names(source: str) -> list[str]:
    """Os nomes de TODAS as funções (``def`` e ``async def``, incluindo as aninhadas e os métodos), na ordem em que aparecem no código. Código inválido: o ``SyntaxError`` sobe."""
    raise NotImplementedError


def imported_modules(source: str) -> list[str]:
    """Os módulos de nível mais alto importados, ordenados e sem repetição: ``import os.path`` -> ``"os"``; ``from collections.abc import Mapping`` -> ``"collections"``;
    ``import a, b`` -> ``"a"`` e ``"b"``. Importações RELATIVAS (``from . import x``, ``from .pacote import y``) NÃO contam. Vale também para imports dentro de funções."""
    raise NotImplementedError


def max_loop_depth(source: str) -> int:
    """A profundidade máxima de aninhamento de laços ``for``, ``async for`` e ``while`` (``0`` se não há laços). Uma função definida dentro de um laço NÃO zera a contagem;
    compreensões (``[x for x in y]``) NÃO contam como laços."""
    raise NotImplementedError


def fold_constants(source: str) -> str:
    """Devolve o código com as contas de constantes INTEIRAS já feitas (só ``+``, ``-`` e ``*``, de baixo para cima), via ``ast.NodeTransformer`` e ``ast.unparse``:
    ``"x = 2 * 3 + y"`` -> ``"x = 6 + y"``; ``"print(1 + 2 * 3)"`` -> ``"print(7)"``. NÃO dobra: ``bool`` (``True + 1``), ``float``, texto, divisão, potência nem operações com variáveis
    (``"y + 1 + 2"`` fica como está, porque a soma de fora é ``(y + 1) + 2``)."""
    raise NotImplementedError
