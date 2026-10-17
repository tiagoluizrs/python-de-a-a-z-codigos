"""Exercício 2: um sinal que NÃO mantém os observadores vivos (``weakref.WeakMethod``), contra o vazamento clássico do Observer."""


class WeakSignal:
    """Observadores que são MÉTODOS LIGADOS (``obj.metodo``) são guardados com ``weakref.WeakMethod``: quando ``obj`` é coletado, o observador some sozinho.
    Funções comuns, ``lambda`` e outros chamáveis são guardados de forma FORTE (como num sinal normal), porque ninguém mais os referencia.

    * ``connect(fn)``: guarda (``fn`` não chamável: ``TypeError("observador precisa ser chamável")``); devolve ``fn``; o mesmo método já conectado (mesmo objeto e
      mesma função): ``ValueError("já conectado")``; para funções fortes, a comparação é por ``==``;
    * ``disconnect(fn)``: remove; desconhecido ou já morto: ``ValueError("não conectado")``;
    * ``emit(*args, **kwargs)``: chama os vivos, na ordem de conexão, e devolve quantos foram chamados; observadores mortos são REMOVIDOS da lista na emissão;
      exceções de um observador NÃO impedem os outros e o PRIMEIRO erro é relançado no fim (``raise`` do próprio erro, não um grupo);
    * ``len(sig)``: quantos observadores estão VIVOS agora (sem precisar de ``emit``)."""

    def __init__(self):
        raise NotImplementedError

    def connect(self, fn):
        raise NotImplementedError

    def disconnect(self, fn) -> None:
        raise NotImplementedError

    def emit(self, *args, **kwargs) -> int:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
