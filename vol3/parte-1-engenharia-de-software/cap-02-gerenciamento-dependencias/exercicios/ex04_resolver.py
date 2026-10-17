"""Exercício 4: um resolvedor com retrocesso."""


class ResolutionError(Exception):
    """Não há combinação de versões que satisfaça tudo."""


def release(text):
    return tuple(int(part) for part in text.split("."))


def satisfies(version, specifier):
    """Pronto: cláusulas ``>=``, ``<=``, ``>``, ``<``, ``==``, ``!=`` separadas
    por vírgula (``""`` aceita tudo)."""
    ops = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b,
           "<": lambda a, b: a < b, "==": lambda a, b: a == b, "!=": lambda a, b: a != b}
    v = release(version)
    for clause in filter(None, (c.strip() for c in specifier.split(","))):
        for op in (">=", "<=", "==", "!=", ">", "<"):
            if clause.startswith(op):
                if not ops[op](v, release(clause[len(op):])):
                    return False
                break
        else:
            raise ValueError(clause)
    return True


def resolve(index, requirements):
    """``index``: ``{pacote: {versão: {dependência: especificador}}}``.
    ``requirements``: ``{pacote: especificador}`` (o que o projeto pede).

    Devolve ``{pacote: versão}`` com TODOS os pacotes necessários (os pedidos
    e os transitivos), escolhendo para cada um a versão MAIS NOVA possível, de
    modo que todas as restrições valham ao mesmo tempo. Se a versão mais nova
    levar a um conflito mais adiante, RETROCEDA e tente a anterior.
    Pacote ausente do índice, ou sem solução, levanta ``ResolutionError``.
    """
    raise NotImplementedError
