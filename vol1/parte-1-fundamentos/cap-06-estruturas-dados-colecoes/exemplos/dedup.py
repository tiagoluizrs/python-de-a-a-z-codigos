"""Remover duplicatas: set perde a ordem, dict.fromkeys preserva."""
items = ["b", "a", "b", "c", "a"]
print(sorted(set(items)))             # set não promete ordem
print(list(dict.fromkeys(items)))     # primeira ocorrência, em ordem
seen = set()
result = []
for item in items:
    if item not in seen:
        seen.add(item)
        result.append(item)
print(result)
# Itens não hasheáveis: use uma chave derivada hasheável
rows = [[1], [2], [1]]
print(list({tuple(r): r for r in rows}.values()))
