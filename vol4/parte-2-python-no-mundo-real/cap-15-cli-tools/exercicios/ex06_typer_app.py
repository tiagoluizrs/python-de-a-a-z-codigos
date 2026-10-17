"""Exercício 6: um app Typer com subcomandos, enum, caminho validado e confirmação."""
import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def resize():
    """Ajuste o tamanho de uma imagem... na verdade, de uma lista de números (sem dependências extras).

    Escreva um comando ``resize`` com estes parâmetros (os TIPOS das anotações fazem a validação):

    * ``numbers``: argumento posicional, uma ou mais ocorrências, ``list[float]`` (``typer.Argument``);
    * ``--scale`` / ``-s``: ``float``, padrão ``1.0``, mínimo ``0.0`` (``min=0``); valores negativos terminam com o
      erro de uso do Typer (código 2);
    * ``--mode``: um ``enum`` (``class Mode(str, Enum)``) com ``round`` e ``floor``, padrão ``round``;
    * ``--verbose`` / ``-v``: flag.

    Para cada número ``x``, escreva ``typer.echo`` do resultado ``x * scale`` arredondado conforme o modo
    (``round(...)`` ou ``math.floor(...)``), um por linha, como ``int``. Com ``--verbose``, antes dos números escreva
    uma linha ``escala=<scale> modo=<mode>`` (``mode`` pelo ``.value``).

    Para o Typer aceitar um único comando como ``app()`` com subcomando, acrescente também um segundo comando
    ``reset`` (sem parâmetros) que escreve ``zerado``."""
    raise NotImplementedError
