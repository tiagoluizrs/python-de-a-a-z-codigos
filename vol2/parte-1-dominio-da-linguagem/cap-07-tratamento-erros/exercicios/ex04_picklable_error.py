"""Exercício 4: exceções que sobrevivem ao pickle."""


class ApiError(Exception):
    """Erro de API com ``status`` e ``message``.

    * ``ApiError(500, "falha")``: ``str(erro) == "500: falha"``;
    * atributos ``status`` e ``message``;
    * ``pickle.loads(pickle.dumps(erro))`` deve devolver uma exceção
      equivalente (mesmo tipo, status, message e str).
    """

    def __init__(self, status, message):
        raise NotImplementedError


class NotFound(ApiError):
    """Subclasse com assinatura PRÓPRIA: ``NotFound("usuário 7")``.

    O status é sempre 404, e o pickle também precisa funcionar
    (dica: ``__reduce__``).
    """

    def __init__(self, message):
        raise NotImplementedError
