"""Exercício 2: nomes de arquivos wheel e escolha da melhor para uma máquina."""


def parse_wheel_filename(filename):
    """``"nome-1.0-py2.py3-none-any.whl"`` ->
    ``{"name": "nome", "version": "1.0", "build": None, "python": ["py2", "py3"],
    "abi": ["none"], "platform": ["any"]}``.

    Formato: ``{nome}-{versão}[-{build}]-{python}-{abi}-{plataforma}.whl`` (5 ou 6
    partes separadas por ``-``; o ``build`` começa com dígito). Os três últimos
    campos podem ter várias opções separadas por ``.``. Levante ``ValueError``
    se não terminar em ``.whl`` ou tiver o número de partes errado."""
    raise NotImplementedError


def expand_tags(info):
    """O conjunto de rótulos ``"python-abi-plataforma"`` que a wheel aceita
    (produto das listas): ``py2.py3`` com ``none`` e ``any`` dá
    ``{"py2-none-any", "py3-none-any"}``."""
    raise NotImplementedError


def best_wheel(filenames, supported):
    """Escolhe, entre ``filenames``, a wheel preferida por um instalador.
    ``supported`` é a lista de rótulos aceitos, do MAIS para o MENOS preferido.
    Ignore o que não for wheel. A vencedora é a que tem um rótulo de MENOR índice
    em ``supported``; empate, a de maior versão numérica (``tuple(int(x) ...)``);
    se nenhuma servir, ``None``."""
    raise NotImplementedError
