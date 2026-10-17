"""Como explorar a biblioteca padrão sem sair do Python."""
import statistics
import sys
import textwrap

# Os módulos da biblioteca padrão, por nome
names = sorted(sys.stdlib_module_names)
print(len(names) > 200, "amostra:", names[100:104])
print("json é stdlib?", "json" in sys.stdlib_module_names)
print("requests é stdlib?", "requests" in sys.stdlib_module_names)

# dir() lista os nomes de um módulo; filtramos os privados
public = [n for n in dir(statistics) if not n.startswith("_")]
print(public[:6])

# A primeira linha do docstring é a ajuda rápida
print(statistics.median.__doc__.splitlines()[0])
print(textwrap.shorten(statistics.fmean.__doc__, width=60))
