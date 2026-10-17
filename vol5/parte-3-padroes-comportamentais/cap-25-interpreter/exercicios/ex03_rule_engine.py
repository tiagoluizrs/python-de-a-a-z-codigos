"""Exercício 3: compilar a regra UMA vez para closures e usar milhares de vezes (um pequeno motor de regras de negócio)."""
import ast


def compile_expr(expression: str):
    """Devolve ``(fn, variables)``: ``fn(ctx)`` avalia a expressão (sintaxe do Python) e ``variables`` é um ``frozenset`` com os nomes usados. A árvore é percorrida SÓ AQUI, na compilação
    (``fn`` NÃO pode chamar ``ast.parse`` nem percorrer o ``ast``: monte closures). O subconjunto permitido:

    * constantes ``None``, ``bool``, ``int``, ``float`` e ``str``; nomes (em ``fn``, fora do ``ctx``: ``KeyError(f"variável indefinida: {nome}")``);
    * ``and`` / ``or`` (semântica do Python: devolvem o operando que decidiu, com curto-circuito) e ``not``; sinal ``-`` unário;
    * ``+``, ``-`` e ``*`` (``/``, ``//``, ``%`` e ``**`` NÃO entram: ``ValueError("expressão não permitida: Div")``, ``"FloorDiv"``, ``"Mod"``, ``"Pow"``);
    * comparações ``== != < <= > >= in not in``, inclusive encadeadas (``18 <= idade < 65``);
    * tuplas e listas literais, que viram ``tuple``.
    Qualquer outra coisa é recusada NA COMPILAÇÃO, com ``ValueError(f"expressão não permitida: {NomeDoNóDoAst}")`` (``"Call"``, ``"Attribute"``...); erro de sintaxe:
    ``ValueError("sintaxe inválida")``."""
    raise NotImplementedError


class Rule:
    """Uma regra nomeada, compilada na CRIAÇÃO (os erros de ``compile_expr`` sobem de lá; nome vazio ou só espaços: ``ValueError("nome vazio")``).

    * atributos ``name``, ``expression`` e ``variables`` (o ``frozenset`` de nomes usados);
    * ``matches(ctx)``: ``bool`` do valor da regra."""

    def __init__(self, name: str, expression: str):
        raise NotImplementedError

    def matches(self, ctx: dict) -> bool:
        raise NotImplementedError


class RuleEngine:
    """Um conjunto de regras.

    * ``add(name, expression)``: cria e guarda a ``Rule`` e a devolve (nome repetido: ``ValueError(f"regra já existe: {name}")``); ``remove(name)``: ``LookupError(name)`` se não existe;
    * ``evaluate(ctx)``: devolve ``{"matched": [...], "errors": {...}}``. ``matched`` tem os nomes das regras verdadeiras, na ORDEM em que foram adicionadas. Uma regra NÃO é avaliada se
      faltar QUALQUER uma das suas ``variables`` no ``ctx`` (mesmo que o curto-circuito dispensasse a variável): ela vai para ``errors[nome] = f"variável indefinida: {x}"`` (``x`` é a
      primeira que falta, em ordem alfabética). Se a avaliação levantar outra exceção (``TypeError`` ao comparar texto com número, por exemplo), ela vai para
      ``errors[nome] = f"{TipoDoErro}: {mensagem}"`` e as OUTRAS regras continuam;
    * ``needed_variables()``: o ``frozenset`` com a união das variáveis de todas as regras; ``len(engine)``: o número de regras."""

    def __init__(self):
        raise NotImplementedError

    def add(self, name: str, expression: str) -> Rule:
        raise NotImplementedError

    def remove(self, name: str) -> None:
        raise NotImplementedError

    def evaluate(self, ctx: dict) -> dict:
        raise NotImplementedError

    def needed_variables(self) -> frozenset:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
