"""Gabarito do exercicio 2: ciclo em grafo de imports."""


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    done: set[str] = set()          # modulos sem ciclo a partir deles
    path: list[str] = []            # caminho em exploracao

    def visit(node: str) -> list[str] | None:
        if node in path:            # voltamos a um modulo da pilha
            start = path.index(node)
            return path[start:] + [node]
        if node in done:
            return None
        path.append(node)
        for dep in graph.get(node, []):
            found = visit(dep)
            if found:
                return found
        path.pop()
        done.add(node)
        return None

    for module in graph:
        found = visit(module)
        if found:
            return found
    return None
