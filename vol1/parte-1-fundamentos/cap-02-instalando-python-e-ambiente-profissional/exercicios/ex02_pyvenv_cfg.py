"""Exercício 2: lendo o arquivo pyvenv.cfg."""


def parse_pyvenv_cfg(text: str) -> dict[str, str]:
    """Converta o conteúdo de um ``pyvenv.cfg`` em um dicionário.

    Cada linha tem o formato ``chave = valor``. Ignore linhas vazias.
    Exemplo: "version = 3.15\nimplementation = CPython"
             -> {'version': '3.15', 'implementation': 'CPython'}
    Cuidado: o valor pode conter o caractere '=' (ex.: um comando).
    """
    raise NotImplementedError
