"""Custo relativo de %, str.format, f-string, Template e concatenação."""
import timeit
from string import Template

name, age, score = "Ana", 31, 9.5
tpl = Template("$name tem $age anos e nota $score")
N = 500_000

cases = {
    "f-string": lambda: f"{name} tem {age} anos e nota {score}",
    "%": lambda: "%s tem %d anos e nota %s" % (name, age, score),
    "str.format": lambda: "{} tem {} anos e nota {}".format(
        name, age, score),
    "format nomeado": lambda: "{n} tem {a} anos e nota {s}".format(
        n=name, a=age, s=score),
    "+ e str()": lambda: (name + " tem " + str(age) + " anos e nota "
                          + str(score)),
    "string.Template": lambda: tpl.substitute(
        name=name, age=age, score=score),
}
for label, fn in cases.items():
    assert fn() == "Ana tem 31 anos e nota 9.5", label
    best = min(timeit.repeat(fn, number=N, repeat=5))
    print(f"{label:16} {best / N * 1e9:7.0f} ns")
