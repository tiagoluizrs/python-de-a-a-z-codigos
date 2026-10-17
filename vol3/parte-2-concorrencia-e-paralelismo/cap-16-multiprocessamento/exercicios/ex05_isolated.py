"""Exercício 5: executar uma função em um processo isolado, com timeout."""


class ProcessCrashed(Exception):
    """O processo filho terminou sem devolver resultado (``exitcode`` guardado)."""

    def __init__(self, exitcode):
        super().__init__(f"processo terminou com exitcode {exitcode}")
        self.exitcode = exitcode


def run_isolated(func, *args, timeout=None):
    """Executa ``func(*args)`` em um processo NOVO (``spawn``) e devolve o resultado.

    * ``func`` e ``args`` precisam ser picklaveis (função de módulo);
    * se a ``func`` levantar uma exceção, ela é re-levantada no pai (o tipo
      original, quando picklável);
    * se passar de ``timeout`` segundos, o filho é TERMINADO e levanta ``TimeoutError``;
    * se o filho morrer sem resultado (``os._exit``), levanta ``ProcessCrashed``
      com o ``exitcode``;
    * use ``tasks.child_main(out, func, args)`` como ``target`` do processo (um
      ``target`` definido neste arquivo não seria importável pelo filho) e uma
      ``Queue`` do contexto ``spawn`` como ``out``;
    * nunca deixe um processo órfão rodando."""
    raise NotImplementedError
