"""Gabarito do exercício 1."""


class Node:
    def __init__(self, name):
        if not name or "/" in name:
            raise ValueError(f"nome inválido: {name!r}")
        self.name, self.parent = name, None

    @property
    def path(self):
        names, node = [], self
        while node is not None:
            names.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(names))

    def size(self):
        raise NotImplementedError

    def count_files(self):
        raise NotImplementedError


class File(Node):
    def __init__(self, name, size):
        super().__init__(name)
        if size < 0:
            raise ValueError("tamanho negativo")
        self._size = size

    def size(self):
        return self._size

    def count_files(self):
        return 1


class Directory(Node):
    def __init__(self, name):
        super().__init__(name)
        self._children = {}

    @property
    def children(self):
        return [self._children[name] for name in sorted(self._children)]

    def add(self, *nodes):
        for node in nodes:
            if node.parent is not None:
                raise ValueError("nó já tem pai")
            ancestor = self
            while ancestor is not None:
                if ancestor is node:
                    raise ValueError("ciclo")
                ancestor = ancestor.parent
            if node.name in self._children:
                raise ValueError(f"já existe: {node.name}")
            node.parent = self
            self._children[node.name] = node
        return self

    def remove(self, name):
        node = self._children.pop(name)
        node.parent = None
        return node

    def walk(self):
        stack = [self]
        while stack:
            node = stack.pop()
            yield node
            if isinstance(node, Directory):
                stack.extend(reversed(node.children))

    def size(self):
        return sum(node.size() for node in self.walk() if isinstance(node, File))

    def count_files(self):
        return sum(1 for node in self.walk() if isinstance(node, File))

    def find(self, predicate):
        return [node.path for node in self.walk() if predicate(node)]

    def depth(self):
        best = 0
        stack = [(self, 1)]
        while stack:
            node, level = stack.pop()
            best = max(best, level)
            if isinstance(node, Directory):
                stack.extend((child, level + 1) for child in node._children.values())
        return best

    def tree(self):
        totals = {}
        for node in reversed(list(self.walk())):
            if isinstance(node, File):
                totals[id(node)] = node.size()
            else:
                totals[id(node)] = sum(totals[id(c)] for c in node._children.values())
        lines = []
        stack = [(self, 0)]
        while stack:
            node, level = stack.pop()
            label = f"{node.name}/ ({totals[id(node)]})" if isinstance(node, Directory) else f"{node.name} ({totals[id(node)]})"
            lines.append("  " * level + label)
            if isinstance(node, Directory):
                stack.extend((child, level + 1) for child in reversed(node.children))
        return "\n".join(lines)
