"""Exercício 3: o objeto camaleão: um ``Null`` que responde a TUDO (e as armadilhas de fazer isso), mais uma busca segura em dados aninhados."""
from collections.abc import Mapping


class Null:
    """Um SINGLETON (``Null() is Null() is NULL``) que absorve qualquer uso:

    * atributo que não existe (``NULL.a.b``): devolve ``NULL``; mas nomes ``__assim__`` (com dois sublinhados nas pontas) levantam ``AttributeError(nome)``: o Python PROCURA esses métodos
      ao copiar, serializar e comparar, e eles não podem virar ``NULL``;
    * chamada (``NULL(1, x=2)``) e índice (``NULL["a"]``) devolvem ``NULL``;
    * ``bool(NULL)`` é ``False``; ``len(NULL)`` é ``0``; iterar não produz nada; ``x in NULL`` é ``False``; ``str(NULL)`` é ``""``; ``repr(NULL)`` é ``"Null"``;
    * igualdade: ``NULL == NULL`` e ``NULL == None`` são ``True``; qualquer outra coisa é ``False`` (inclusive ``NULL == 0``); ``hash(NULL)`` é ``hash(None)``;
    * as operações ``+ - * /`` (``a + NULL`` e ``NULL + a``, e as outras três também) devolvem ``NULL``;
    * é IMUTÁVEL: atribuir ou apagar um atributo levanta ``AttributeError("Null é imutável")``;
    * funciona em ``with`` (``__enter__`` devolve ``NULL``; ``__exit__`` devolve ``False``);
    * ``copy.copy(NULL)`` e ``copy.deepcopy(NULL)`` devolvem o MESMO ``NULL``."""

    def __new__(cls):
        raise NotImplementedError


NULL = None                                                    # troque por ``Null()`` quando a classe estiver pronta


def is_null(value) -> bool:
    """``True`` só para o próprio ``NULL`` (um ``None`` NÃO é ``NULL``)."""
    raise NotImplementedError


def dig(obj, path: str, default=None):
    """Busca segura em dados aninhados: ``dig({"a": {"b": 1}}, "a.b")`` é ``1``. ``path`` separa os passos por ``"."``. Em cada passo: se o objeto atual é um ``Mapping``, usa a chave;
    senão, usa ``getattr``. Passo que não existe (``KeyError``/``AttributeError``): devolve ``default`` NA HORA. Um valor que EXISTE é devolvido como está, mesmo ``0``, ``""``, ``False``
    ou ``None`` (``default`` só vale para ausência). Caminho vazio (``""``): devolve ``obj``. As chaves do dicionário são TEXTO (``"a"``); índice de lista: não suportado
    (a lista não é ``Mapping`` e ``getattr(lista, "0")`` não existe: devolve ``default``)."""
    raise NotImplementedError
