"""Exercício 4: um registro PREGUIÇOSO: guarda o caminho ("pacote.modulo:atributo") e só importa quando alguém pede."""
import importlib
import threading


class LazyRegistry:
    """Um catálogo nome -> alvo, em que o alvo pode ser um TEXTO ``"pacote.modulo:atributo"`` (importado só no primeiro ``get``) ou um objeto qualquer (já carregado).

    * ``register(name, target, *, replace=False)``: nome já registrado (e ``replace`` falso): ``ValueError(f"já registrado: {name}")``; um ``target`` que é ``str`` precisa ter EXATAMENTE
      um ``":"`` com texto (sem espaços nas pontas) dos dois lados: ``ValueError(f"caminho inválido: {target!r}")``; ``replace=True`` troca o alvo e ESQUECE o objeto já carregado;
    * ``get(name)``: desconhecido: ``KeyError(f"desconhecido: {name!r}; disponíveis: a, b")`` (ordem alfabética, ``nenhum`` se vazio). Um alvo ``str`` é carregado com
      ``importlib.import_module(modulo)`` (chame pelo módulo ``importlib``, não por uma cópia da função) e depois ``getattr`` para cada parte do atributo, separando por ``"."``
      (``"collections:OrderedDict.fromkeys"`` funciona). O resultado fica em cache: o ``get`` seguinte NÃO importa de novo;
    * falha ao carregar (``ImportError`` ou ``AttributeError``): ``LookupError(f"não pôde ser carregado: {name!r} ({TipoDoErro}: {mensagem})")`` com a causa original (``from``); a falha NÃO
      fica em cache: se o módulo passar a existir, o ``get`` seguinte funciona;
    * ``names()`` (todos, ordenados), ``loaded()`` (os já carregados, ordenados; um alvo que não era ``str`` conta como carregado desde o registro), ``is_loaded(name)``,
      ``preload(*names)`` (carrega os pedidos, ou TODOS se não houver argumentos, e devolve a lista ordenada dos nomes carregados agora), ``name in reg``, ``len(reg)``;
    * THREADS: duas threads pedindo o mesmo nome ao mesmo tempo importam o módulo UMA vez só (use uma trava)."""

    def __init__(self):
        raise NotImplementedError

    def register(self, name: str, target, *, replace: bool = False) -> None:
        raise NotImplementedError

    def get(self, name: str):
        raise NotImplementedError

    def names(self) -> list[str]:
        raise NotImplementedError

    def loaded(self) -> list[str]:
        raise NotImplementedError

    def is_loaded(self, name: str) -> bool:
        raise NotImplementedError

    def preload(self, *names: str) -> list[str]:
        raise NotImplementedError

    def __contains__(self, name) -> bool:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
