"""Exercício 2: transação com rollback usando @contextmanager."""


def transaction(store):
    """Context manager (escrito como GERADOR com ``@contextmanager``).

    * ao entrar, guarda uma cópia de ``store`` (um dict) e devolve o
      próprio ``store`` para o ``as``;
    * se o bloco terminar normalmente, mantém as mudanças (commit);
    * se levantar exceção, restaura o conteúdo ORIGINAL do mesmo dict
      (``clear`` + ``update``, para quem guardou a referência ver o
      rollback) e RELANÇA a exceção.

    Lembre do ``try``: sem ele, o código depois do ``yield`` não roda
    quando o bloco falha.
    """
    raise NotImplementedError


def suppress_and_count(*exception_types):
    """Context manager que suprime ``exception_types`` e conta quantas vezes
    suprimiu.

    Devolva um objeto com o atributo ``count`` (inicialmente 0) via ``as``.
    Exceções de outros tipos continuam subindo. Pode ser escrito como classe
    ou como gerador.
    """
    raise NotImplementedError
