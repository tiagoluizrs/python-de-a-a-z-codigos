"""Exercício 5: traduzir erros de sistema em erros do domínio."""


class StorageError(Exception):
    """Erro genérico de armazenamento (guarde o ``errno`` em ``.errno``)."""


class ResourceMissing(StorageError):
    pass


class AccessDenied(StorageError):
    pass


class DecodeFailure(StorageError):
    pass


def read_text_or_explain(path):
    """Leia ``path`` como UTF-8 e devolva o texto.

    Traduza (sempre encadeando com ``from``):

    * ``FileNotFoundError``  -> ``ResourceMissing``
    * ``PermissionError``    -> ``AccessDenied``
    * ``UnicodeDecodeError`` -> ``DecodeFailure``
    * qualquer outro ``OSError`` -> ``StorageError`` com ``.errno`` copiado

    Use as SUBCLASSES de OSError, e não comparações de ``errno``.
    """
    raise NotImplementedError
