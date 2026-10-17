"""Exercício 1: converter variáveis de ambiente (tudo chega como texto)."""


def as_bool(text, name="valor"):
    """``"1"``, ``"true"``, ``"yes"``, ``"on"`` (sem diferenciar caixa, sem espaços
    nas pontas) -> ``True``; ``"0"``, ``"false"``, ``"no"``, ``"off"`` e vazio ->
    ``False``. Outro texto: ``ValueError(f"{name}: booleano inválido: {text!r}")``."""
    raise NotImplementedError


def as_int(text, name="valor", minimum=None, maximum=None):
    """``int(text)`` (aceita espaços e sinal). Texto inválido, ou fora de
    ``[minimum, maximum]`` (quando dados): ``ValueError`` cuja mensagem COMEÇA com
    ``f"{name}: "``. Rejeite ``bool``-textos como ``"True"`` (é inválido)."""
    raise NotImplementedError


def as_list(text, separator=",", cast=str):
    """Divide ``text`` por ``separator``, remove espaços e ITENS VAZIOS, aplica
    ``cast`` a cada item. Texto vazio -> ``[]``. Erro de ``cast`` propaga."""
    raise NotImplementedError


def as_duration(text, name="valor"):
    """Duração em SEGUNDOS (``float``): ``"90"`` (segundos), ``"30s"``, ``"5m"``,
    ``"2h"``, ``"1d"``, ``"1.5h"``, ``"500ms"``. Espaços tolerados
    (``"5 m"``). Inválido ou negativo: ``ValueError`` começando com ``f"{name}: "``."""
    raise NotImplementedError
