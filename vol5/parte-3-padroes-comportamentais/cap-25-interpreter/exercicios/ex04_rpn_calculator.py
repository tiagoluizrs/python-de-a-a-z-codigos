"""Exercício 4: um interpretador SEM classes: a calculadora de pilha (notação polonesa reversa), com tabela de despacho e palavras definidas pelo usuário."""
import operator

BINARY = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv, "//": operator.floordiv, "%": operator.mod, "**": operator.pow, "max": max, "min": min}
UNARY = {"neg": operator.neg, "abs": abs}


def rpn(text: str, variables: dict | None = None, words: dict | None = None):
    """Interpreta ``text`` (palavras separadas por espaço) e devolve o ÚNICO valor que sobra na pilha.

    Para cada palavra, nesta ORDEM: (1) um número (tente ``int`` e depois ``float``) é empilhado; (2) um operador de ``BINARY`` tira ``b`` e depois ``a`` da pilha e empilha ``a op b``;
    (3) um de ``UNARY`` transforma o topo; (4) as palavras de pilha ``dup`` (copia o topo), ``swap`` (troca os dois do topo), ``drop`` (descarta o topo) e ``over`` (``a b`` -> ``a b a``);
    (5) uma PALAVRA DO USUÁRIO (``words``: ``{"sq": "dup *"}``) é um macro: o texto dela roda na MESMA pilha; (6) uma variável de ``variables`` empilha o valor dela;
    (7) qualquer outra: ``ValueError(f"palavra desconhecida: {palavra}")``.

    Erros: faltando operandos para uma palavra: ``ValueError(f"pilha vazia em: {palavra}")``; macros que se chamam em mais de 50 níveis: ``ValueError("recursão demais")``;
    no fim, pilha vazia: ``ValueError("expressão vazia")`` e mais de um valor: ``ValueError("sobraram valores na pilha")``; a divisão por zero levanta o ``ZeroDivisionError`` normal."""
    raise NotImplementedError


def rpn_trace(text: str, variables: dict | None = None, words: dict | None = None) -> list[list]:
    """Uma lista com a pilha (UMA CÓPIA) depois de CADA palavra do ``text`` (uma palavra do usuário conta como um passo só). Não confere o tamanho final da pilha.
    ``rpn_trace("3 4 + 2 *")`` é ``[[3], [3, 4], [7], [7, 2], [14]]``. Os erros são os de ``rpn``."""
    raise NotImplementedError
