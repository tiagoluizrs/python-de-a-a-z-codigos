"""Ponto de entrada de linha de comando."""
import sys

from . import greeting


def main():
    print(greeting(sys.argv[1] if len(sys.argv) > 1 else "mundo"))
