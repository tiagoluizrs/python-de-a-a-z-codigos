"""Exercício 4: regras como objetos para VALIDAR: todas as falhas de uma vez (e não só a primeira), com regras condicionais."""


class ValidationError(Exception):
    """(Pronto, NÃO edite.) ``ValidationError(errors)``: guarda a lista em ``.errors``; ``str(erro)`` é as mensagens unidas por ``"; "``."""

    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = list(errors)


class Rule:
    """``Rule(check, message, when=None)``.

    * ``check(item)`` devolve ``True`` se o item está OK; ``message`` é um texto OU uma função ``message(item)`` que o devolve; ``when(item)`` (opcional): a regra SÓ vale se ``when``
      for verdadeira (senão ela passa);
    * ``error(item)``: ``None`` se a regra passa (ou não se aplica); senão a mensagem. Uma exceção levantada por ``check``, ``when`` ou ``message`` sobe sem ser tratada."""

    def __init__(self, check, message, when=None):
        raise NotImplementedError

    def error(self, item) -> str | None:
        raise NotImplementedError


class Validator:
    """Uma lista ordenada de regras.

    * ``Validator(rules=())``; ``add(rule)``: acrescenta e devolve o PRÓPRIO validador (para encadear);
    * ``validate(item)``: a lista das mensagens de TODAS as regras que falharam, na ordem das regras (``[]`` se está tudo certo);
    * ``is_valid(item)``: ``True`` se ``validate`` é vazia;
    * ``first_error(item)``: a primeira mensagem ou ``None``; PARA na primeira falha (as regras seguintes nem são avaliadas);
    * ``ensure(item)``: devolve o ``item`` se é válido; senão levanta ``ValidationError(erros)`` com todas as mensagens."""

    def __init__(self, rules=()):
        raise NotImplementedError

    def add(self, rule: Rule) -> "Validator":
        raise NotImplementedError

    def validate(self, item) -> list[str]:
        raise NotImplementedError

    def is_valid(self, item) -> bool:
        raise NotImplementedError

    def first_error(self, item) -> str | None:
        raise NotImplementedError

    def ensure(self, item):
        raise NotImplementedError


def required(field: str) -> Rule:
    """O campo (chave do dicionário) existe e não é ``None`` nem texto vazio (só espaços também conta como vazio). Mensagem: ``f"{field} é obrigatório"``. ``0`` e ``False`` são valores válidos."""
    raise NotImplementedError


def min_value(field: str, minimum) -> Rule:
    """``item[field] >= minimum``. Campo ausente ou ``None``: PASSA (para exigir, use ``required``). Mensagem: ``f"{field} deve ser >= {minimum}"``."""
    raise NotImplementedError


def max_len(field: str, maximum: int) -> Rule:
    """``len(item[field]) <= maximum``. Campo ausente ou ``None``: passa. Mensagem: ``f"{field} deve ter no máximo {maximum} caracteres"``."""
    raise NotImplementedError
