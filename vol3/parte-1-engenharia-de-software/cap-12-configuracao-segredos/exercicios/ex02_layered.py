"""Exercício 2: configuração em camadas, com proveniência."""


def load_settings(defaults, file_data=None, environ=None, cli=None, prefix="APP_"):
    """Combina quatro fontes (a ÚLTIMA da lista vence): ``defaults`` < ``file_data``
    < ``environ`` < ``cli``. Devolve ``(settings, sources)``: o dict final e um dict
    ``{chave: "default" | "file" | "env" | "cli"}``.

    * só chaves presentes em ``defaults`` são aceitas; chave desconhecida em
      ``file_data`` ou ``cli`` levanta ``KeyError(chave)``; em ``environ``, só
      variáveis com ``prefix`` contam e as de nome desconhecido são IGNORADAS;
    * nomes do ambiente: ``APP_DB_URL`` -> ``db_url`` (sem o prefixo, em minúsculas);
    * o valor do ambiente é TEXTO e deve ser convertido para o TIPO do padrão
      (``bool``: ``true/1/yes/on`` e ``false/0/no/off``; ``int``; ``float``;
      ``list`` -> separar por vírgula; ``str``). Falha na conversão levanta
      ``ValueError`` com o nome da variável original;
    * valores de ``cli`` igual a ``None`` são ignorados (opção não dada).
    """
    raise NotImplementedError
