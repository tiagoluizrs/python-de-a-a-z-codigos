"""Exercício 2: a precedência de configuração de uma CLI (flag > ambiente > arquivo > padrão)."""


def resolve(name: str, flags: dict, env: dict, file_values: dict, defaults: dict, convert=str, prefix: str = "APP_"):
    """Resolve o valor de ``name`` e diz DE ONDE ele veio.

    Ordem de precedência: ``flags[name]`` (se a chave existir e o valor NÃO for ``None``: flag que o usuário não
    passou chega como ``None``), depois ``env[prefix + name.upper()]`` (variável de ambiente, sempre texto), depois
    ``file_values[name]`` e por último ``defaults[name]``.

    Devolve ``(valor, origem)`` com ``origem`` em ``"flag"``, ``"env"``, ``"arquivo"`` ou ``"padrão"``. Aplique
    ``convert`` ao valor SÓ quando ele vem do ambiente (flags e arquivo já têm o tipo certo; o padrão também).
    Se ``convert`` falhar (``ValueError``), levante ``ValueError`` com a mensagem
    ``"APP_PORT: valor inválido 'abc'"`` (o nome da variável, com o prefixo, e o ``repr`` do valor). Se o nome não
    estiver em lugar nenhum, levante ``KeyError(name)``."""
    raise NotImplementedError


def resolve_all(names: list[str], flags: dict, env: dict, file_values: dict, defaults: dict, converters: dict | None = None):
    """Aplica ``resolve`` a cada nome de ``names`` (com ``converters.get(name, str)``) e devolve dois dicts:
    ``(valores, origens)``, na ordem de ``names``."""
    raise NotImplementedError
