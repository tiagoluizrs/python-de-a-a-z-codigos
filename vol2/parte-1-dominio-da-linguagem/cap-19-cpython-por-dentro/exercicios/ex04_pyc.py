"""Exercício 4: ler e escrever arquivos .pyc."""


def read_pyc_header(path):
    """Lê o cabeçalho (16 bytes) de um ``.pyc`` e devolve um dict com
    ``magic`` (``bytes``, 4), ``flags`` (``int``), ``mtime`` (``int``) e
    ``size`` (``int``, tamanho do fonte). Se o ``magic`` não for o do
    interpretador atual (``importlib.util.MAGIC_NUMBER``), levanta
    ``ValueError``."""
    raise NotImplementedError


def load_pyc(path):
    """Devolve o objeto de código guardado no ``.pyc`` (após o cabeçalho de
    16 bytes), com ``marshal.loads``."""
    raise NotImplementedError


def is_fresh(source_path, pyc_path):
    """``True`` se o ``.pyc`` é válido para o fonte: ``mtime`` e ``size`` do
    cabeçalho iguais ao ``os.stat`` do fonte (``int(st_mtime)`` e
    ``st_size``). Só considere o modo por data (``flags == 0``); outro valor de
    ``flags`` devolve ``False``."""
    raise NotImplementedError
