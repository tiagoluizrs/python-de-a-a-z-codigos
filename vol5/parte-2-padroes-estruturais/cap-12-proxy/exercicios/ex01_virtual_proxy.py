"""Exercício 1: um proxy VIRTUAL (preguiçoso) quase transparente: atributos e métodos especiais passam para o objeto real, criado só no primeiro uso."""


class LazyProxy:
    """``LazyProxy(factory)``: ``factory()`` cria o objeto real na PRIMEIRA vez que algo precisa dele.

    Delegue ao objeto real (carregando-o se preciso): atributos (leitura, escrita e ``del``), ``len``, ``iter``, ``[]`` (leitura, escrita e ``del``), ``in``,
    ``bool``, ``str``, ``==``, ``hash``, chamada (``proxy(...)``), ``with`` (``__enter__``/``__exit__``) e ``__class__`` (uma ``property``, para que
    ``isinstance(proxy, list)`` funcione). Regras:

    * ``repr``: ``"<LazyProxy não carregado>"`` se ainda não carregou (e SEM carregar); depois, ``f"<LazyProxy {alvo!r}>"``;
    * ``==``: compara o alvo com ``other`` (se ``other`` também é um ``LazyProxy``, compare com o alvo dele); ``hash(proxy) == hash(alvo)``;
    * ``is_loaded``: propriedade do próprio proxy (``True`` depois de carregar); ``unwrap()``: devolve o alvo (carregando); ``reset()``: esquece o alvo
      (o próximo uso chama a fábrica de novo);
    * se ``factory`` levantar uma exceção, ela sobe e NADA fica guardado (o próximo uso tenta de novo);
    * seguro com threads: com 8 threads usando o proxy ao mesmo tempo, ``factory`` roda UMA vez (trava com dupla verificação);
    * os atributos internos do próprio proxy (``_factory``, ``_target``, ``_lock``) devem ser guardados com ``object.__setattr__`` e NÃO podem passar pelo alvo.
    Os nomes ``is_loaded``, ``unwrap`` e ``reset`` pertencem ao proxy (um alvo com esses nomes fica inacessível por ele; de propósito)."""

    def __init__(self, factory):
        raise NotImplementedError

    def __getattr__(self, name):
        raise NotImplementedError

    def __setattr__(self, name, value):
        raise NotImplementedError

    def __delattr__(self, name):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __contains__(self, item):
        raise NotImplementedError

    def __bool__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, *exc):
        raise NotImplementedError

    @property
    def __class__(self):
        raise NotImplementedError

    @property
    def is_loaded(self) -> bool:
        raise NotImplementedError

    def unwrap(self):
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError
