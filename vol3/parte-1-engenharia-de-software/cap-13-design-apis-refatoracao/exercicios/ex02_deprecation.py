"""Exercício 2: depreciar com graça."""
import warnings  # noqa: F401


def deprecated(since, removal, alternative=None):
    """Decorador de FUNÇÃO. Ao chamar a função decorada, emite
    ``DeprecationWarning`` com a mensagem
    ``"<nome> está obsoleta desde <since> e será removida na <removal>"`` e, se
    ``alternative`` for dado, ``"; use <alternative>"`` ao final, com
    ``stacklevel=2`` (o aviso aponta para QUEM CHAMOU). Preserva ``__name__``,
    ``__doc__`` e o resultado; acrescenta ao fim do ``__doc__`` a linha
    ``"\\n\\nObsoleta desde <since>."`` (se ``__doc__`` for ``None``, começa por vazio)."""
    raise NotImplementedError


def renamed_parameter(old, new, since):
    """Decorador: a função passou a chamar ``new`` o parâmetro que se chamava
    ``old``. Quem ainda passa ``old=...`` por nome continua funcionando: o valor é
    repassado como ``new`` e um ``DeprecationWarning`` (``stacklevel=2``) avisa
    ``"parâmetro 'old' foi renomeado para 'new' na versão <since>"``. Passar os
    dois ao mesmo tempo levanta ``TypeError(f"não use {old!r} e {new!r} juntos")``."""
    raise NotImplementedError
