"""Exercício 4: um comando em Click (opções validadas, saída para humanos e para máquinas)."""
import click


@click.command()
def stats():
    """Estatísticas de uma coluna numérica de um CSV.

    Uso: ``stats ARQUIVO.csv --column nota [--format text|json] [--skip-invalid]``

    * ``ARQUIVO`` é obrigatório e precisa EXISTIR (use ``click.Path(exists=True, dir_okay=False)``);
    * ``--column`` / ``-c`` (obrigatória): o nome da coluna (cabeçalho do CSV);
    * ``--format`` (``click.Choice``): ``text`` (padrão) ou ``json``;
    * ``--skip-invalid`` (flag): ignora valores que não são números; sem ela, um valor inválido encerra com
      ``click.ClickException`` (código de saída 1; mensagem ``linha <n>: valor inválido '<texto>'``, em que ``n`` é a
      linha do arquivo contando o cabeçalho como linha 1);
    * coluna inexistente: ``click.ClickException(f"coluna {nome!r} não existe (colunas: a, b, c)")``;
    * saída ``text``: uma linha por estatística, ``n=3``, ``min=1.0``, ``max=3.0``, ``mean=2.0`` (uma por linha, nesta
      ordem); saída ``json``: um objeto com as mesmas chaves (``n`` inteiro, o resto ``float``), em uma linha
      (``json.dumps`` sem ``indent``). Sem nenhum valor válido: ``click.ClickException("nenhum valor numérico")``.

    Escreva com ``click.echo`` (o ``CliRunner`` captura)."""
    raise NotImplementedError
