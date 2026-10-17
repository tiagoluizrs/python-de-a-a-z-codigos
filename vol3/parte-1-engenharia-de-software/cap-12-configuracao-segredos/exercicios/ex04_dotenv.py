"""Exercício 4: ler um arquivo .env."""


def parse_dotenv(text, environ=None):
    """Interpreta o texto de um ``.env`` e devolve ``dict[str, str]``.

    Regras: linhas em branco e que começam com ``#`` são ignoradas; ``CHAVE=valor``
    (espaços ao redor de ``=`` e nas pontas são removidos); prefixo opcional
    ``export ``; valor entre aspas DUPLAS interpreta ``\\n`` e ``\\"``; entre aspas
    SIMPLES é literal; sem aspas, um ``" #"`` inicia comentário (corta o resto);
    ``${NOME}`` é expandido com valores definidos ANTES no arquivo, ou em
    ``environ`` (dict, padrão ``{}``), ou ``""`` se não existir (NÃO expanda dentro
    de aspas simples). Uma chave sem ``=`` ou com nome inválido
    (``[A-Za-z_][A-Za-z0-9_]*``) levanta ``ValueError`` com ``"linha N"``."""
    raise NotImplementedError
