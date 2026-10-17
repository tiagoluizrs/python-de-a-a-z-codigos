"""Mostra as duas tabelas de um dict: índices (esparsa) e entradas."""
from dictpeek import inspect_dict


def show(title, d):
    info = inspect_dict(d)
    print(f"--- {title}")
    print("slots:", info["slots"], "| cabem:",
          info["usable"] + info["nentries"], "| usadas:",
          info["nentries"], "| bytes por entrada:", info["entry_size"])
    print("índices :", info["indices"])
    print("entradas:", info["entries"])


d = {10: "a", 20: "b", 30: "c"}
show("três chaves int", d)

# Colisão: 0, 8 e 16 caem no mesmo slot (hash & 7 == 0)
show("colisões", {0: "x", 8: "y", 16: "z"})

# Chaves str: a entrada guarda só (chave, valor), 16 bytes
show("chaves str", {"x": 1, "y": 2})

# Remoção: o slot vira -2 (lápide) e a entrada vira um buraco
d = {i: i for i in range(5)}
del d[2]
show("depois de del d[2]", d)

# A ordem de iteração é a ordem do vetor de entradas
d[2] = "volta"
print("ordem:", list(d))
show("depois de d[2] = ... (vai para o fim)", d)
