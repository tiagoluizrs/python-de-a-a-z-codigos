"""Exercício 3: um mediador reativo: valores derivados recalculados em CASCATA, sem laços infinitos."""


class Store:
    """Valores base e valores DERIVADOS de outros.

    * ``Store(**initial)``: os valores base iniciais;
    * ``set(key, value)``: altera um valor BASE; valor igual ao atual (``==``): NÃO faz nada (nenhum derivado é recalculado e nenhum observador é chamado); chave que é derivada:
      ``ValueError("derivado não pode ser alterado")``; chave nova (ainda inexistente) é criada como base;
    * ``derive(name, fn, *deps)``: define ``name`` como ``fn(valor_de_dep1, valor_de_dep2, ...)``, calculado AGORA e recalculado quando qualquer dependência mudar; as dependências podem ser
      valores base OU outros derivados (propagação em CASCATA, em ordem topológica: um derivado só é recalculado DEPOIS de todas as suas dependências já atualizadas, e UMA vez por ``set``);
      dependência inexistente: ``KeyError(dep)``; ``name`` já existe (base ou derivado): ``ValueError(f"já existe: {name}")``; um CICLO (``name`` entre as suas dependências diretas ou
      indiretas) não pode ocorrer porque as dependências precisam existir ANTES, mas ``name in deps`` deve levantar ``ValueError("ciclo")``;
    * ``get(name)``: o valor atual (``KeyError`` se não existe); ``store[name]`` é o mesmo;
    * ``watch(name, callback)``: chama ``callback(old, new)`` quando o valor de ``name`` (base OU derivado) MUDA de verdade (``!=``), na ordem do registro; devolve o ``callback``;
      ``name`` inexistente: ``KeyError``;
    * ``recomputed``: lista (cópia) com os nomes dos derivados recalculados desde a última ``clear_log()``; ``clear_log()`` a esvazia."""

    def __init__(self, **initial):
        raise NotImplementedError

    def set(self, key: str, value) -> None:
        raise NotImplementedError

    def derive(self, name: str, fn, *deps: str) -> None:
        raise NotImplementedError

    def get(self, name: str):
        raise NotImplementedError

    def __getitem__(self, name: str):
        raise NotImplementedError

    def watch(self, name: str, callback):
        raise NotImplementedError

    @property
    def recomputed(self) -> list[str]:
        raise NotImplementedError

    def clear_log(self) -> None:
        raise NotImplementedError
