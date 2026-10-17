"""greeter: cumprimenta com um modelo guardado em um arquivo de dados do pacote."""
from importlib.resources import files


def greeting(name):
    template = files("greeter").joinpath("data/template.txt").read_text(encoding="utf-8").strip()
    return f"{template} {name}!"
