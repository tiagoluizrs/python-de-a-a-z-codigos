"""Atribuição, cópia rasa e cópia profunda."""
import copy

original = {"name": "ana", "tags": ["a", "b"], "pos": (1, 2)}

alias = original                      # nenhuma cópia
shallow = copy.copy(original)         # contêiner novo, itens compartilhados
deep = copy.deepcopy(original)        # tudo novo (recursivamente)

original["tags"].append("c")
original["name"] = "bia"

print("alias  :", alias["name"], alias["tags"])
print("shallow:", shallow["name"], shallow["tags"])
print("deep   :", deep["name"], deep["tags"])
print("shallow['tags'] is original['tags']:",
      shallow["tags"] is original["tags"])
print("deep['tags'] is original['tags']   :",
      deep["tags"] is original["tags"])

# Outras formas de cópia rasa
items = [[1], [2]]
for clone in (items[:], list(items), items.copy(), [*items]):
    print(clone == items, clone is items, clone[0] is items[0])

# Imutáveis atômicos: deepcopy devolve o próprio objeto
t = (1, "a", 2.5)
print("tupla atômica:", copy.deepcopy(t) is t)
t2 = (1, [2])
print("tupla com lista:", copy.deepcopy(t2) is t2)
