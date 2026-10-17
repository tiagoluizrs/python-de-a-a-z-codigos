"""Exercício 5: validar muitos registros sem parar no primeiro erro."""


def validate_records(model, rows):
    """Valida cada dicionário de ``rows`` com ``model.model_validate``. Devolve ``(validos, erros)``:

    * ``validos``: lista de instâncias, na ordem de entrada (só as que passaram);
    * ``erros``: lista de dicionários ``{"index": i, "errors": [{"loc": "a.b", "type": "...", "msg": "..."}, ...]}``,
      um por registro inválido, com ``loc`` já junto por pontos;
    * uma linha com problema NÃO interrompe as outras; ``rows`` vazio devolve ``([], [])``."""
    raise NotImplementedError


def validate_json_lines(model, text):
    """Valida um texto em JSON Lines (um objeto JSON por linha; linhas vazias são ignoradas). Devolve ``(validos, erros)`` como acima,
    mas ``index`` é o NÚMERO DA LINHA (1-based, contando as vazias); JSON inválido vira um erro com
    ``{"loc": "", "type": "json_invalid", "msg": ...}``. Use ``model.model_validate_json`` para cada linha."""
    raise NotImplementedError
