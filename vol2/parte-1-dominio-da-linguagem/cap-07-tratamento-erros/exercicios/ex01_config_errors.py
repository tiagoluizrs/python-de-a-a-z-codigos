"""Exercício 1: erros de domínio com encadeamento."""


class ConfigError(Exception):
    """Base de todos os erros desta biblioteca."""


class InvalidValueError(ConfigError):
    """Valor que não é um inteiro."""

    def __init__(self, line_no, key, raw):
        raise NotImplementedError


class MissingSeparatorError(ConfigError):
    """Linha sem o sinal de igual."""

    def __init__(self, line_no, line):
        raise NotImplementedError


def parse_settings(lines):
    """Converta linhas ``chave = inteiro`` em um dict.

    * ignore linhas vazias e as que começam com ``#``;
    * linha sem ``=`` levanta ``MissingSeparatorError(line_no, line)``;
    * valor que não é inteiro levanta ``InvalidValueError(line_no, key, raw)``
      ENCADEADO ao ``ValueError`` original (``raise ... from``);
    * ``line_no`` começa em 1 e conta TODAS as linhas, inclusive as ignoradas;
    * o texto (``str(erro)``) deve ser ``"linha 3: valor inválido para 'port': 'x'"``
      e ``"linha 2: falta '=' em 'abc'"``.
    """
    raise NotImplementedError
