"""Exercício 1: o Composite clássico (arquivos e pastas), com travessia ITERATIVA (aguenta árvores mais fundas que o limite de recursão)."""


class Node:
    """Base: ``name`` (não vazio e sem ``"/"``, senão ``ValueError(f"nome inválido: {name!r}")``) e ``parent`` (``None`` na raiz)."""

    def __init__(self, name: str):
        raise NotImplementedError

    @property
    def path(self) -> str:
        """O caminho a partir da raiz: ``"/raiz"``, ``"/raiz/src/main.py"`` (a raiz da árvore a que o nó pertence entra no caminho). Iterativo."""
        raise NotImplementedError

    def size(self) -> int:
        raise NotImplementedError

    def count_files(self) -> int:
        raise NotImplementedError


class File(Node):
    """``File(name, size)``: ``size`` inteiro ``>= 0`` (senão ``ValueError("tamanho negativo")``). ``size()`` devolve o tamanho; ``count_files()`` devolve 1."""

    def __init__(self, name: str, size: int):
        raise NotImplementedError


class Directory(Node):
    """``Directory(name)``. Operações (TODAS as que percorrem a árvore devem ser ITERATIVAS, sem recursão; os testes usam cadeias de 5.000 níveis):

    * ``add(*nodes)``: acrescenta cada nó, define o ``parent`` e devolve ``self`` (para encadear). Erros, nesta ordem: o nó já tem pai
      (``ValueError("nó já tem pai")``); o nó é ``self`` ou um ANCESTRAL de ``self`` (``ValueError("ciclo")``); já existe um filho com esse nome
      (``ValueError(f"já existe: {nome}")``). Se um erro ocorrer, os nós anteriores da mesma chamada já foram acrescentados;
    * ``remove(name)``: remove e devolve o filho (com ``parent = None``); inexistente: ``KeyError(name)``;
    * ``children``: lista dos filhos EM ORDEM ALFABÉTICA de nome (uma cópia: alterá-la não altera a pasta);
    * ``size()``: soma dos tamanhos de tudo; ``count_files()``: quantos arquivos há na subárvore;
    * ``walk()``: gerador que produz ``self`` e todos os descendentes em PRÉ-ORDEM (cada pasta antes do conteúdo), com os filhos em ordem alfabética;
    * ``find(predicate)``: lista dos ``path`` dos nós (de ``walk()``) para os quais ``predicate(nó)`` é verdadeiro, na ordem de ``walk()``;
    * ``depth()``: a profundidade da subárvore (``self`` sozinho = 1; uma pasta vazia = 1; uma pasta com um arquivo = 2);
    * ``tree()``: o desenho em texto, uma linha por nó, 2 espaços por nível: ``"nome/ (tamanho_total)"`` para pastas e ``"nome (tamanho)"`` para arquivos, na ordem
      de ``walk()``, separadas por ``\\n``."""

    def __init__(self, name: str):
        raise NotImplementedError

    @property
    def children(self) -> list:
        raise NotImplementedError

    def add(self, *nodes):
        raise NotImplementedError

    def remove(self, name: str):
        raise NotImplementedError

    def size(self) -> int:
        raise NotImplementedError

    def count_files(self) -> int:
        raise NotImplementedError

    def walk(self):
        raise NotImplementedError

    def find(self, predicate) -> list[str]:
        raise NotImplementedError

    def depth(self) -> int:
        raise NotImplementedError

    def tree(self) -> str:
        raise NotImplementedError
