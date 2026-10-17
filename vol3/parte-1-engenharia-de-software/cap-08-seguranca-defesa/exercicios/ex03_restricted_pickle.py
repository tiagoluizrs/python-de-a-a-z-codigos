"""Exercício 3: pickle com lista de permissão."""
import io
import pickle


def restricted_loads(data, allowed=frozenset()):
    """Carrega ``data`` (bytes de um pickle) permitindo SOMENTE as classes e
    funções em ``allowed`` (conjunto de pares ``(módulo, nome)``).

    Estruturas simples (``dict``, ``list``, ``tuple``, ``str``, ``int``,
    ``float``, ``bool``, ``None``, ``bytes``) não precisam de permissão. Qualquer
    outra referência a objeto global (``os.system``, ``builtins.print``, ``set``
    se não permitido...) levanta ``pickle.UnpicklingError`` com a mensagem
    ``"proibido: <módulo>.<nome>"``. Use uma subclasse de ``pickle.Unpickler``
    e sobrescreva ``find_class``."""
    raise NotImplementedError
