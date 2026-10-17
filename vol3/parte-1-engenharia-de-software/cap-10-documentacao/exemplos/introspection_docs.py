"""Um gerador de referência de API em Markdown, só com inspect (o que o Sphinx e o pdoc fazem por baixo)."""
import inspect

import shapes


def describe(obj):
    doc = inspect.getdoc(obj) or "(sem documentação)"
    return doc.splitlines()[0]


print(f"# {shapes.__name__}\n\n{describe(shapes)}\n")
for name in shapes.__all__:
    obj = getattr(shapes, name)
    kind = "classe" if inspect.isclass(obj) else "função"
    try:
        signature = str(inspect.signature(obj))
    except (TypeError, ValueError):
        signature = "()"
    print(f"## `{name}{signature}` ({kind})\n\n{describe(obj)}\n")
    if inspect.isclass(obj):
        for method_name, method in inspect.getmembers(obj, inspect.isfunction):
            if not method_name.startswith("_"):
                print(f"- `{method_name}{inspect.signature(method)}`: {describe(method)}")
        print()
