"""Exercício 4: comandos como DADOS: registrar, gravar em JSON e reproduzir (o germe do *event sourcing*)."""
import json


class CommandRegistry:
    """Guarda manipuladores (funções) por nome. Um manipulador é ``handler(state, **args) -> novo_estado`` (puro: devolve o novo estado, não altera o recebido).

    * ``handler(name)``: DECORADOR que registra a função sob ``name`` (devolve a função); nome já usado: ``ValueError(f"comando já registrado: {name}")``;
    * ``execute(state, command)``: ``command`` é um dict ``{"name": str, "args": dict}`` (``args`` opcional, padrão ``{}``); devolve ``handler(state, **args)``;
      formato inválido (não é dict, sem ``name`` ou ``args`` que não é dict): ``ValueError("comando inválido")``; nome desconhecido:
      ``KeyError(f"comando desconhecido: {nome}")``;
    * ``replay(state, log)``: aplica os comandos de ``log`` em ordem, encadeando os estados, e devolve o estado final; uma falha sobe com o ÍNDICE do comando:
      levante ``RuntimeError(f"comando {i} falhou: {erro}")`` com ``from erro`` (``i`` a partir de 0), mas só para ``Exception`` de dentro do manipulador; os erros de
      formato e de comando desconhecido sobem como são."""

    def __init__(self):
        raise NotImplementedError

    def handler(self, name: str):
        raise NotImplementedError

    def execute(self, state, command: dict):
        raise NotImplementedError

    def replay(self, state, log: list):
        raise NotImplementedError


class Journal:
    """O diário: executa comandos E os registra. ``Journal(registry, state)``.

    * ``apply(command)``: executa (``registry.execute``) sobre o estado atual e, SE der certo, atualiza ``state`` e acrescenta o comando ao log; se falhar, estado e log
      ficam como estavam e a exceção sobe;
    * ``state``: o estado atual; ``log``: uma CÓPIA da lista de comandos aplicados (cada um também copiado: alterar o que ``log`` devolve não altera o diário);
    * ``dumps()``: o log como texto JSON (``json.dumps(log, sort_keys=True)``); ``Journal.loads(registry, initial_state, text)`` reconstrói um ``Journal``
      reaplicando os comandos do texto sobre ``initial_state``;
    * ``state_at(initial_state, n)``: o estado depois dos ``n`` primeiros comandos do log, a partir de ``initial_state`` (``n`` fora de ``0..len(log)``:
      ``ValueError("n fora do intervalo")``)."""

    def __init__(self, registry: CommandRegistry, state):
        raise NotImplementedError

    def apply(self, command: dict) -> None:
        raise NotImplementedError

    @property
    def state(self):
        raise NotImplementedError

    @property
    def log(self) -> list:
        raise NotImplementedError

    def dumps(self) -> str:
        raise NotImplementedError

    @classmethod
    def loads(cls, registry: CommandRegistry, initial_state, text: str) -> "Journal":
        raise NotImplementedError

    def state_at(self, initial_state, n: int):
        raise NotImplementedError
