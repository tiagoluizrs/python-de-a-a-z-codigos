"""Gabarito do exercício 4."""
from collections import deque


class Node:
    def __init__(self, value):
        self.value, self.left, self.right = value, None, None


class BST:
    def __init__(self, values=()):
        self._root, self._size = None, 0
        for value in values:
            self.add(value)

    def add(self, value):
        if self._root is None:
            self._root = Node(value)
            self._size = 1
            return True
        node = self._root
        while True:
            if value == node.value:
                return False
            side = "left" if value < node.value else "right"
            child = getattr(node, side)
            if child is None:
                setattr(node, side, Node(value))
                self._size += 1
                return True
            node = child

    def __iter__(self):
        stack, node = [], self._root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            yield node.value
            node = node.right

    def __len__(self):
        return self._size

    def __contains__(self, value):
        node = self._root
        while node is not None:
            if value == node.value:
                return True
            node = node.left if value < node.value else node.right
        return False

    def preorder(self):
        stack = [self._root] if self._root else []
        while stack:
            node = stack.pop()
            yield node.value
            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)

    def postorder(self):
        stack, last = [], None
        node = self._root
        while stack or node is not None:
            if node is not None:
                stack.append(node)
                node = node.left
            else:
                top = stack[-1]
                if top.right is not None and last is not top.right:
                    node = top.right
                else:
                    yield top.value
                    last = stack.pop()

    def levelorder(self):
        queue = deque([self._root] if self._root else [])
        while queue:
            node = queue.popleft()
            yield node.value
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    def height(self):
        best = 0
        stack = [(self._root, 1)] if self._root else []
        while stack:
            node, level = stack.pop()
            best = max(best, level)
            for child in (node.left, node.right):
                if child:
                    stack.append((child, level + 1))
        return best

    def min(self):
        if self._root is None:
            raise ValueError("árvore vazia")
        node = self._root
        while node.left:
            node = node.left
        return node.value

    def max(self):
        if self._root is None:
            raise ValueError("árvore vazia")
        node = self._root
        while node.right:
            node = node.right
        return node.value

    def range(self, low, high):
        stack, node = [], self._root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left if node.value >= low else None
            node = stack.pop()
            if node.value > high:
                return
            if node.value >= low:
                yield node.value
            node = node.right
