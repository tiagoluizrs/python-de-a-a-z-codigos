"""Exercício 3: templates com ``@contextmanager``: o esqueleto (preparar, tentar, limpar) fica na função e o passo variável é o corpo do ``with``."""
from contextlib import contextmanager


@contextmanager
def transaction(store: dict):
    """Faz uma CÓPIA do dicionário ``store`` ao entrar e a devolve com ``yield`` (o mesmo ``store`` também pode ser usado). Se o corpo levantar uma exceção, RESTAURA ``store`` ao
    conteúdo de antes (``clear`` + ``update``, sem trocar o objeto) e deixa a exceção subir; se terminar bem, mantém as alterações (confirma). ``yield`` entrega o próprio ``store``."""
    raise NotImplementedError


@contextmanager
def temporary_attr(obj, name: str, value):
    """Define ``obj.name = value`` durante o ``with`` e RESTAURA ao sair (mesmo com exceção): se o atributo existia, volta ao valor antigo; se não existia, é APAGADO
    (``delattr``). Atributos de ``__slots__`` ou propriedades sem ``setter`` falham como falhariam normalmente."""
    raise NotImplementedError


@contextmanager
def collect_errors(errors: list, *exceptions):
    """Engole as exceções das classes dadas em ``exceptions`` (sem classes: ``Exception``), acrescentando cada uma à lista ``errors`` e continuando o programa depois do ``with``;
    outras exceções sobem normalmente. Nada é engolido de ``KeyboardInterrupt`` e ``SystemExit`` (que não são ``Exception``) a menos que estejam em ``exceptions``."""
    raise NotImplementedError


@contextmanager
def ordered_cleanup(log: list, name: str):
    """O esqueleto de recurso: acrescenta ``f"abrir {name}"`` ao ``log`` ao entrar (e ``yield name``), e ``f"fechar {name}"`` ao sair, SEMPRE (mesmo com exceção);
    se o corpo levantar, acrescenta ainda ``f"erro em {name}: {tipo}"`` (com o ``__name__`` da exceção) ANTES de ``fechar`` e deixa a exceção subir."""
    raise NotImplementedError


def run_steps(steps, log: list) -> list:
    """O Template Method como função: para cada ``(name, fn)`` de ``steps`` executa ``fn()`` dentro de ``ordered_cleanup(log, name)``; devolve a lista dos resultados na ordem.
    Se um passo levantar, os seguintes NÃO rodam, e a exceção sobe (o ``log`` já tem o ``abrir``, o ``erro`` e o ``fechar`` do que falhou)."""
    raise NotImplementedError
