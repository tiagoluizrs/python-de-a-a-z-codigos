"""Exercício 3: medir memória "profunda" (``sys.getsizeof`` recursivo, sem contar duas vezes o mesmo objeto) para comparar representações."""
import sys


def deep_size(obj, _seen: set | None = None) -> int:
    """O tamanho em bytes de ``obj`` e de tudo que ele alcança, contando CADA objeto uma única vez (por ``id``):

    * ``sys.getsizeof(obj)`` do próprio objeto;
    * contêineres: ``list``, ``tuple``, ``set``, ``frozenset`` e ``deque`` somam os elementos; ``dict`` soma as chaves E os valores;
    * objetos comuns somam o ``__dict__`` (se existir; o dict é um objeto como outro qualquer) e os valores dos atributos de ``__slots__`` (percorra
      ``type(obj).__mro__`` procurando ``__slots__``, com ``getattr`` e ignorando os não definidos);
    * ``str``, ``bytes``, ``int``, ``float``, ``bool``, ``None`` e outros atômicos: só o ``getsizeof``;
    * ``_seen`` (um ``set`` de ``id``s) é como você evita contar de novo (e evita laços): se ``id(obj)`` já está nele, devolve 0.
    Pode ser recursivo (as estruturas dos testes são rasas)."""
    raise NotImplementedError


def per_object(factories: dict, n: int) -> dict[str, float]:
    """Para cada ``nome -> factory`` de ``factories``, constrói uma lista com ``n`` objetos (``[factory(i) for i in range(n)]``) e devolve
    ``{nome: deep_size(lista) / n}`` (bytes por objeto, ``round(..., 1)``). ``n < 1``: ``ValueError("n deve ser >= 1")``."""
    raise NotImplementedError


def savings_ratio(before: float, after: float) -> float:
    """Quantas vezes MENOS memória: ``round(before / after, 2)``. ``after <= 0``: ``ValueError("after deve ser positivo")``."""
    raise NotImplementedError


def shared_fraction(objects: list) -> float:
    """A fração de objetos de ``objects`` que são compartilhados, isto é, que aparecem MAIS de uma vez na lista (por identidade): ``1 - distintos / total``
    (``round(..., 3)``); lista vazia: ``0.0``. Exemplo: ``[a, a, b]`` -> ``0.333``."""
    raise NotImplementedError
