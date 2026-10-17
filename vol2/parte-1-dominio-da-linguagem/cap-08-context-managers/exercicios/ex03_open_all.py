"""Exercício 3: abrir uma quantidade dinâmica de arquivos com ExitStack."""


def read_all(paths, opener=open):
    """Abra TODOS os arquivos de ``paths`` ao mesmo tempo e devolva a lista
    de seus conteúdos (``handle.read()``), na ordem.

    * use ``contextlib.ExitStack`` e ``opener(path)`` (``open`` por padrão);
    * se algum arquivo não puder ser aberto, os que já foram abertos devem
      ser FECHADOS e a exceção original deve subir;
    * ao terminar normalmente, todos os arquivos devem estar fechados.
    """
    raise NotImplementedError
