"""Exercício 1: um contador seguro entre threads."""


class SafeCounter:
    """Contador compartilhado.

    * ``SafeCounter(start=0, on_step=None)``; ``on_step`` (um callable sem
      argumentos, ou ``None``) é chamado ENTRE a leitura e a escrita dentro de
      ``add`` (é como o teste abre uma "janela" para expor corridas);
    * ``add(n=1)``: soma ``n`` e devolve o NOVO valor (leia, chame ``on_step``,
      escreva), de forma atômica entre threads;
    * ``value`` (propriedade): o valor atual;
    * ``compare_and_set(expected, new)``: se o valor atual for ``expected``, troca
      por ``new`` e devolve ``True``; senão ``False`` (atômico);
    * ``update(func)``: aplica ``func`` ao valor atual e grava o resultado,
      atomicamente (``func`` pode demorar), e devolve o novo valor."""

    def __init__(self, start=0, on_step=None):
        raise NotImplementedError
