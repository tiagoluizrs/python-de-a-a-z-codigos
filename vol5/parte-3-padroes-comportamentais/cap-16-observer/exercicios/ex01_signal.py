"""Exercício 1: um ``Signal`` (a lista de funções do Observer) robusto: cópia na emissão, ``once``, exceções agrupadas."""


class Signal:
    """Uma lista de observadores (funções).

    * ``connect(fn, *, once=False)``: acrescenta ``fn`` e a DEVOLVE (serve como decorador, inclusive ``@sig.connect`` sem argumentos); ``fn`` não chamável:
      ``TypeError("observador precisa ser chamável")``; já conectada: ``ValueError("já conectado")``; com ``once=True``, ela é desconectada automaticamente
      depois da PRIMEIRA vez que for chamada;
    * ``disconnect(fn)``: remove; não conectada: ``ValueError("não conectado")``;
    * ``emit(*args, **kwargs)``: chama os observadores NA ORDEM de conexão e devolve quantos foram chamados. A lista percorrida é uma CÓPIA tirada no início da
      emissão: quem for desconectado durante a emissão ainda é chamado NESTA emissão, e quem for conectado durante a emissão só é chamado na próxima. Se
      observadores levantarem ``Exception``, TODOS os outros ainda são chamados e, no fim, é levantado um ``ExceptionGroup("observadores falharam", erros)``
      com as exceções na ordem em que ocorreram (nesse caso nada é devolvido);
    * ``len(sig)``: quantos observadores estão conectados; ``fn in sig``: se está conectada."""

    def __init__(self):
        raise NotImplementedError

    def connect(self, fn=None, *, once: bool = False):
        raise NotImplementedError

    def disconnect(self, fn) -> None:
        raise NotImplementedError

    def emit(self, *args, **kwargs) -> int:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __contains__(self, fn) -> bool:
        raise NotImplementedError
