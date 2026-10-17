"""Exercício 2: reaproveitar a gramática do Python: um avaliador com LISTA BRANCA sobre o ``ast`` (nada de ``eval``!)."""
import ast


def safe_eval(expression: str, ctx: dict | None = None):
    """Avalia ``expression`` (sintaxe do Python) com as variáveis de ``ctx``, permitindo SÓ este subconjunto:

    * constantes ``None``, ``bool``, ``int``, ``float`` e ``str`` (``bytes``, números complexos e ``...`` NÃO: ``ValueError("expressão não permitida: Constant")``);
    * nomes (variáveis de ``ctx``; fora dele: ``KeyError(f"variável indefinida: {nome}")``);
    * ``and`` / ``or`` com a semântica do Python (devolvem o OPERANDO que decidiu, com curto-circuito) e ``not``; sinais unários ``-`` e ``+``;
    * aritmética ``+ - * / // % **`` SÓ entre números (``int``, ``float`` ou ``bool``; senão ``ValueError("operandos devem ser números")``); o expoente de ``**`` com valor absoluto
      acima de 100: ``ValueError("expoente grande demais")``; a divisão por zero levanta o ``ZeroDivisionError`` normal;
    * comparações ``== != < <= > >= in not in``, inclusive ENCADEADAS (``18 <= idade < 65``); ``is`` e ``is not`` NÃO são permitidos;
    * tuplas, listas e conjuntos literais (``(1, 2)``, ``[1, 2]``, ``{1, 2}``), que viram ``tuple``, ``list`` e ``set``.

    Qualquer outra coisa (chamadas, atributos, índices, ``lambda``, compreensões, f-strings, ``if`` em linha, ``:=``...): ``ValueError(f"expressão não permitida: {NomeDoNóDoAst}")``,
    como ``"Call"``, ``"Attribute"``, ``"Subscript"``, ``"Lambda"``, ``"ListComp"``, ``"JoinedStr"``, ``"IfExp"``; o operador de comparação proibido também: ``"Is"``.

    A árvore INTEIRA é validada ANTES de qualquer avaliação: ``safe_eval("False and open('x')")`` já é recusada, mesmo que o curto-circuito nunca chegasse na chamada.
    Texto com mais de 1.000 caracteres: ``ValueError("expressão grande demais")`` (antes de analisar); erro de sintaxe: ``ValueError("sintaxe inválida")``."""
    raise NotImplementedError
