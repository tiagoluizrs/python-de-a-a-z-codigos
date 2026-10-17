"""A mesma função documentada em três estilos, e como o Python guarda e mostra a documentação."""
import inspect
import pydoc
import subprocess
import sys


def google_style(items, factor=1.0):
    """Multiplica cada item por um fator.

    Args:
        items: Números a multiplicar.
        factor: O fator. Padrão ``1.0``.

    Returns:
        Uma lista com os produtos.

    Raises:
        TypeError: Se algum item não for número.
    """
    return [i * factor for i in items]


def numpy_style(items, factor=1.0):
    """Multiplica cada item por um fator.

    Parameters
    ----------
    items : list of float
        Números a multiplicar.
    factor : float, optional
        O fator (padrão 1.0).

    Returns
    -------
    list of float
        Os produtos.
    """
    return [i * factor for i in items]


def rest_style(items, factor=1.0):
    """Multiplica cada item por um fator.

    :param items: Números a multiplicar.
    :param factor: O fator. Padrão ``1.0``.
    :returns: Uma lista com os produtos.
    :raises TypeError: Se algum item não for número.
    """
    return [i * factor for i in items]


for fn in (google_style, numpy_style, rest_style):
    print(f"{fn.__name__:<13} -> {len(inspect.getdoc(fn).splitlines())} linhas | primeira linha: {inspect.getdoc(fn).splitlines()[0]!r}")

# A docstring é um ATRIBUTO do objeto
print("__doc__ é o texto cru:", repr(google_style.__doc__[:30]), "| getdoc limpa a indentação:", repr(inspect.getdoc(google_style)[:30]))

# help() e pydoc usam a mesma fonte
rendered = pydoc.render_doc(google_style, renderer=pydoc.plaintext)
print(rendered.splitlines()[2:5])

# Com -OO as docstrings DESAPARECEM (economia de memória; não dependa delas em tempo de execução)
code = "def f():\n    \"\"\"documentada\"\"\"\nprint(f.__doc__)"
for flags in ([], ["-OO"]):
    out = subprocess.run([sys.executable, *flags, "-c", code], capture_output=True, text=True).stdout.strip()
    print(f"python {' '.join(flags):<4} -> f.__doc__ = {out!r}")
