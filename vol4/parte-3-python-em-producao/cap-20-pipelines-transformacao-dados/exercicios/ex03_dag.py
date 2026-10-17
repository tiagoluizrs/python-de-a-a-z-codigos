"""Exercício 3: um orquestrador de DAG pequeno e determinístico (sem threads): ordem, cache por conteúdo, falhas e recomeço."""
from dataclasses import dataclass, field


@dataclass
class Task:
    name: str
    fn: object                                  # callable: recebe as SAÍDAS das dependências, na ordem de ``deps``
    deps: list = field(default_factory=list)
    retries: int = 0                            # tentativas EXTRAS (retries=2: até 3 execuções)
    version: str = "1"                          # mude para invalidar o cache quando o CÓDIGO da tarefa mudar


def execution_order(tasks: list[Task]) -> list[str]:
    """Ordem topológica estável: entre as tarefas prontas, sempre a de MENOR nome primeiro. Dependência que não existe:
    ``ValueError("<tarefa> depende de <dep>, que não existe")``; ciclo: ``ValueError("ciclo: a -> b -> a")`` (o caminho, começando no
    menor nome que participa dele, voltando a ele no fim). Nome de tarefa repetido: ``ValueError``."""
    raise NotImplementedError


def run(tasks: list[Task], cache: dict) -> dict:
    """Executa as tarefas na ordem de ``execution_order`` e devolve ``{"outputs": {nome: saída}, "log": [(nome, status), ...],
    "failed": [nomes], "skipped": [nomes]}``.

    * a CHAVE de cache de uma tarefa é uma tupla ``(nome, version, chaves_das_dependências)``, em que ``chaves_das_dependências`` é a
      tupla das chaves de cache das suas dependências, na ordem de ``deps`` (assim, uma mudança em uma origem invalida tudo o que
      depende dela, e nada mais);
    * se a chave está em ``cache`` (um dict que o CHAMADOR guarda entre as chamadas), a saída vem de lá e o status é ``"cache"``;
    * senão executa ``fn(*saidas)``: sucesso -> grava no ``cache`` e status ``"ok"``; se levantar exceção e ainda houver ``retries``,
      tenta de novo; esgotadas, status ``"falhou"`` (NÃO grava no cache) e o nome entra em ``failed``;
    * uma tarefa cuja dependência falhou ou foi pulada NÃO executa: status ``"pulada"`` e o nome entra em ``skipped``;
    * tarefas independentes de uma que falhou continuam normalmente."""
    raise NotImplementedError
