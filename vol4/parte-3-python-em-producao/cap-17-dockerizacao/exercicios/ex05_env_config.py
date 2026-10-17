"""Exercício 5: configuração por variáveis de ambiente (12-factor) e segredos em arquivo (``*_FILE``)."""


class ConfigError(Exception):
    """Reúne TODOS os problemas de configuração em uma mensagem (``problems`` é a lista)."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("; ".join(problems))


def load_config(env: dict, spec: dict) -> dict:
    """Lê a configuração de ``env`` (um dict de textos, como ``os.environ``) segundo ``spec``.

    ``spec`` mapeia o NOME da variável para um dict com as chaves opcionais ``type`` (``str`` por padrão; ``int``, ``float``,
    ``bool``), ``default`` (se ausente na ``spec``, a variável é OBRIGATÓRIA), ``secret`` (``bool``, padrão ``False``) e
    ``read_file`` (um callable ``caminho -> texto`` para ler arquivos; só usado com ``*_FILE``).

    Regras:

    * valor vem de ``env[NOME]``; se não existir e existir ``env[NOME + "_FILE"]``, o valor é ``read_file(caminho)`` com as
      quebras de linha do FIM removidas (é como os *secrets* do Docker chegam); se os DOIS existirem, é um problema:
      ``"NOME: defina NOME ou NOME_FILE, não os dois"``;
    * sem valor e sem ``default``: ``"NOME: obrigatória"``; sem valor e com ``default``: usa o ``default`` (sem converter);
    * conversão: ``int``/``float`` com ``int(...)``/``float(...)``; ``bool`` aceita ``1/true/yes/on`` e ``0/false/no/off``
      (sem diferenciar maiúsculas de minúsculas); outro texto: ``"NOME: valor inválido '<texto>' para <tipo>"``;
    * NÃO pare no primeiro problema: junte todos e levante ``ConfigError`` ao final (ordem da ``spec``);
    * devolva um dict ``{NOME: valor}`` na ordem da ``spec``."""
    raise NotImplementedError


def describe(config: dict, spec: dict) -> str:
    """Um texto seguro para o log: uma linha ``NOME=valor`` por variável (ordem da ``spec``), mas com ``***`` no lugar do
    valor das que têm ``secret=True`` (``"DB_PASSWORD=***"``)."""
    raise NotImplementedError
