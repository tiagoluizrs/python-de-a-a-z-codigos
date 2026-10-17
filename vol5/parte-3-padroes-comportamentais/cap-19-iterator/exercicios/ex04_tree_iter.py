"""Exercício 4: iteradores de uma árvore binária de busca, SEM recursão (aguentam árvores de milhares de níveis)."""


class Node:
    def __init__(self, value):
        self.value, self.left, self.right = value, None, None


class BST:
    """Uma árvore binária de busca. Sem valores repetidos (``add`` de um valor que já existe não faz nada e devolve ``False``; senão ``True``). TODAS as operações que
    percorrem a árvore devem ser ITERATIVAS (os testes usam uma árvore degenerada de 3.000 níveis, que estoura a recursão).

    * ``BST(values=())``: acrescenta cada valor em ordem; ``add(value)``;
    * ``__iter__``: em ORDEM (crescente), como um GERADOR com pilha explícita; ``__len__``; ``__contains__`` (busca descendo pela árvore, sem percorrer tudo);
    * ``preorder()``, ``postorder()`` e ``levelorder()`` (por níveis, da esquerda para a direita; use ``collections.deque``): geradores dos valores;
    * ``height()``: ``0`` se vazia, ``1`` com um nó, etc.; ``min()`` e ``max()``: o menor e o maior valor (``ValueError("árvore vazia")`` se vazia);
    * ``range(low, high)``: gerador dos valores com ``low <= valor <= high``, em ordem, PODANDO os ramos que não podem conter nada do intervalo (a árvore do teste conta
      quantos nós foram visitados)."""

    def __init__(self, values=()):
        raise NotImplementedError

    def add(self, value) -> bool:
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __contains__(self, value) -> bool:
        raise NotImplementedError

    def preorder(self):
        raise NotImplementedError

    def postorder(self):
        raise NotImplementedError

    def levelorder(self):
        raise NotImplementedError

    def height(self) -> int:
        raise NotImplementedError

    def min(self):
        raise NotImplementedError

    def max(self):
        raise NotImplementedError

    def range(self, low, high):
        raise NotImplementedError
