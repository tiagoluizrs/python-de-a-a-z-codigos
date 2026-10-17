"""Exercício 4: uma cadeia de BUSCA em camadas com ``collections.ChainMap`` (CLI > ambiente > arquivo > padrões)."""
from collections import ChainMap


class LayeredConfig:
    """``LayeredConfig(**layers)``: cada argumento nomeado é uma CAMADA (um ``dict``), da MAIS prioritária para a MENOS (a ordem dos argumentos nomeados): por exemplo
    ``LayeredConfig(cli={...}, env={...}, file={...}, defaults={...})``. Sem camadas: ``ValueError("sem camadas")``.

    * ``config[key]`` e ``config.get(key, default=None)``: a PRIMEIRA camada que tem a chave responde (``KeyError(key)`` em ``[]`` se nenhuma tem); as camadas dadas são COPIADAS
      (alterar o dict original depois não afeta a configuração);
    * ``source(key)``: o NOME da camada que responde por ``key`` (``KeyError`` se nenhuma);
    * ``config[key] = value``: grava na camada MAIS prioritária (a primeira) e nunca nas outras;
    * ``layers``: lista dos nomes na ordem de prioridade;
    * ``override(**values)``: devolve uma NOVA ``LayeredConfig`` com uma camada ``"override"`` no TOPO contendo ``values`` (a original não muda e não vê a camada nova);
    * ``without(key)``: devolve uma nova ``LayeredConfig`` em que ``key`` NÃO existe em nenhuma camada (copiando as camadas sem ela; a original não muda);
    * ``flatten()``: um dict comum com o valor vencedor de cada chave (ordem: chaves da camada de MENOR prioridade primeiro, como o ``dict(ChainMap)``); ``shadowed(key)``: a lista de
      ``(camada, valor)`` de TODAS as camadas que têm ``key``, da mais para a menos prioritária (inclusive as que perderam);
    * ``len(config)`` é o número de chaves distintas; ``key in config``; iteração pelas chaves."""

    def __init__(self, **layers):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def get(self, key, default=None):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __contains__(self, key) -> bool:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def source(self, key) -> str:
        raise NotImplementedError

    @property
    def layers(self) -> list[str]:
        raise NotImplementedError

    def override(self, **values) -> "LayeredConfig":
        raise NotImplementedError

    def without(self, key) -> "LayeredConfig":
        raise NotImplementedError

    def flatten(self) -> dict:
        raise NotImplementedError

    def shadowed(self, key) -> list[tuple[str, object]]:
        raise NotImplementedError
