"""Exercício 2: um contêiner de injeção com auto-wiring (o que os frameworks fazem): lê as anotações de tipo do construtor e monta o grafo sozinho."""
import functools
import inspect
from contextlib import contextmanager
from typing import get_type_hints


class Container:
    """Uma fábrica de objetos que resolve as dependências pelos TIPOS.

    * ``register(key, factory=None, *, lifetime="singleton")``: ``key`` é uma classe (o tipo pedido); ``factory`` é uma classe ou uma função que cria o objeto (padrão: o próprio ``key``).
      ``lifetime`` é ``"singleton"`` (UM objeto, criado na primeira vez) ou ``"transient"`` (um NOVO a cada ``resolve``); outro valor: ``ValueError(f"lifetime inválido: {lifetime}")``;
      registrar a mesma chave de novo substitui o registro anterior (e esquece o singleton antigo);
    * ``register_instance(key, obj)``: registra um objeto JÁ pronto (sempre devolvido como está) e o devolve; ``has(key)``: ``True`` se há registro, instância ou ``override`` para a chave;
    * ``resolve(key)``: devolve o objeto. Os parâmetros da fábrica são lidos com ``typing.get_type_hints`` e ``inspect.signature`` (para classes, os do ``__init__`` sem ``self``):
        - parâmetro com tipo REGISTRADO (ou com ``override``): resolvido pelo contêiner, recursivamente (mesmo que tenha valor padrão: o contêiner vence);
        - tipo não registrado, MAS com valor padrão: usa o padrão; sem valor padrão: ``LookupError(f"não registrado: {Tipo} (cadeia: A -> Tipo)")`` (``A -> B -> Tipo``: a cadeia
          desde o que foi pedido);
        - sem anotação e sem padrão: ``TypeError(f"parâmetro sem tipo: {Chave}.{parametro}")``;
      ``key`` não registrada, pedida direto: ``LookupError(f"não registrado: {Key}")`` (sem a cadeia); ciclo: ``RuntimeError("dependência circular: A -> B -> A")``;
      os nomes dos tipos são ``__name__``;
    * a análise da assinatura de cada fábrica é feita UMA vez (cache): resolver o mesmo grafo ``transient`` 50 vezes não inspeciona 50 vezes;
    * uma exceção dentro da fábrica sobe e NADA fica em cache para ela;
    * ``override(key, instance)``: gerenciador de contexto: dentro do ``with``, ``resolve(key)`` devolve ``instance`` (e quem depende de ``key`` a recebe), mesmo para chave não registrada;
      ao ENTRAR e ao SAIR os singletons já criados são DESCARTADOS (senão um singleton antigo continuaria apontando para a dependência velha, ou para o dublê, depois do ``with``)."""

    def __init__(self):
        raise NotImplementedError

    def register(self, key, factory=None, *, lifetime: str = "singleton") -> None:
        raise NotImplementedError

    def register_instance(self, key, obj):
        raise NotImplementedError

    def has(self, key) -> bool:
        raise NotImplementedError

    def resolve(self, key, _chain: tuple = ()):
        raise NotImplementedError

    @contextmanager
    def override(self, key, instance):
        raise NotImplementedError
        yield
