"""Gabarito do exercício 5."""


class StorageError(Exception):
    def __init__(self, message, errno=None):
        super().__init__(message)
        self.errno = errno


class ResourceMissing(StorageError):
    pass


class AccessDenied(StorageError):
    pass


class DecodeFailure(StorageError):
    pass


def read_text_or_explain(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError as error:                 # subclasse antes da geral
        raise ResourceMissing(f"não existe: {path}", error.errno) from error
    except PermissionError as error:
        raise AccessDenied(f"sem permissão: {path}", error.errno) from error
    except UnicodeDecodeError as error:
        raise DecodeFailure(f"não é UTF-8: {path}") from error
    except OSError as error:                           # o resto da família
        raise StorageError(f"erro de sistema em {path}: {error.strerror}",
                           error.errno) from error
