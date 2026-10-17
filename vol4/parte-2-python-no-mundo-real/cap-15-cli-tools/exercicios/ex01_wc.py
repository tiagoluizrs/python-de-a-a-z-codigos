"""Exercício 1: um ``wc`` com argparse, testável (entrada e saídas são injetadas)."""
import io
import sys


def main(argv: list[str], stdin=None, stdout=None, stderr=None) -> int:
    """Conta linhas, palavras e bytes, como o ``wc``.

    * ``ARQUIVO...`` posicionais (``nargs="*"``); sem nenhum, ou o nome ``-``, lê ``stdin`` (um ``io.BytesIO`` ou
      ``sys.stdin.buffer`` quando for ``None``);
    * ``-l`` (linhas: quantidade de ``\\n``), ``-w`` (palavras: ``len(bytes.split())``) e ``-c`` (bytes). Sem nenhuma
      das três flags, mostra as três, nesta ordem: linhas, palavras, bytes. Com várias flags, mantenha sempre a
      ordem linhas, palavras, bytes;
    * saída: para cada arquivo, os números alinhados à direita em largura 7, separados por um espaço, e depois o
      nome (``"      3       5      21 a.txt"``); para ``-`` (stdin sem nome), só os números. Com mais de um arquivo,
      uma última linha com os totais e o nome ``total``;
    * arquivo inexistente: mensagem ``wc: <nome>: arquivo ou diretório inexistente`` em ``stderr``, SEGUE com os
      outros, e o código de saída final é ``1`` (``0`` se tudo deu certo). Uso incorreto (flag desconhecida): o
      ``argparse`` termina com ``SystemExit(2)`` (deixe subir);
    * escreva em ``stdout``/``stderr`` recebidos (``sys.stdout`` e ``sys.stderr`` quando ``None``), nunca com ``print``
      sem o argumento ``file``.

    Devolve o código de saída (``int``)."""
    raise NotImplementedError
