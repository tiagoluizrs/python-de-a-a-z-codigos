"""Exercício 6: validar toda a configuração na partida."""


class ConfigError(Exception):
    """Reúne TODOS os problemas (``.problems``: lista de textos)."""

    def __init__(self, problems):
        super().__init__("configuração inválida: " + "; ".join(problems))
        self.problems = problems


def validate_settings(settings, schema):
    """Confere ``settings`` (dict) contra ``schema``: ``{nome: regras}``, onde
    ``regras`` pode ter ``"type"`` (``int``, ``str``, ``bool``, ``float``),
    ``"required"`` (padrão ``False``), ``"default"``, ``"min"``, ``"max"``,
    ``"choices"``.

    Devolve um dict NOVO com os valores finais (defaults aplicados). Colete TODOS
    os problemas antes de falhar (``ConfigError``), com mensagens:
    ``"<nome>: obrigatório"``, ``"<nome>: esperado <tipo>, recebido <tipo recebido>"``
    (``bool`` NÃO vale como ``int``), ``"<nome>: menor que <min>"``,
    ``"<nome>: maior que <max>"``, ``"<nome>: valor fora de <choices>"`` (escreva
    ``list(choices)``), ``"<nome>: chave desconhecida"`` para chaves em ``settings``
    que não estão no schema. A ordem dos problemas: a do ``schema`` e, por
    último, as chaves desconhecidas em ordem alfabética."""
    raise NotImplementedError


def describe(settings, secret_keys=()):
    """Texto de uma linha para LOG: ``"chave=valor"`` ordenado por chave, separado
    por ``", "``; as chaves em ``secret_keys`` aparecem como ``"chave=***"``."""
    raise NotImplementedError
