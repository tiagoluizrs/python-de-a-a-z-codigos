"""Exercício 2: um objeto com um recurso que não se copia: ``__copy__`` e ``__deepcopy__``."""
import threading


class Report:
    """``Report(title, sections)``: ``title`` (texto) e ``sections`` (lista). Mais dois atributos PRIVADOS criados no ``__init__``:

    * ``_lock``: uma ``threading.Lock()`` (não pode ser copiada);
    * ``_cache``: começa ``None``; ``render()`` calcula ``f"{title}: " + ", ".join(sections)``, guarda em ``_cache`` e devolve (as chamadas
      seguintes devolvem o ``_cache``, mesmo que ``sections`` tenha mudado: é um cache de propósito).

    Cópias (``copy.copy`` e ``copy.deepcopy``) devem funcionar:

    * ``__copy__``: nova instância do MESMO tipo (``type(self)``, subclasses incluídas, sem chamar ``__init__``), compartilhando ``sections``
      (cópia rasa), com um ``_lock`` NOVO e ``_cache`` igual a ``None``;
    * ``__deepcopy__(memo)``: o mesmo, mas ``sections`` copiada em profundidade (use o ``memo``: ``copy.deepcopy(self.sections, memo)``) e registre
      a nova instância em ``memo[id(self)]`` ANTES de copiar o conteúdo;
    * ``with_changes(**changes)``: devolve uma cópia RASA (``copy.copy``) com os atributos ``title`` e/ou ``sections`` trocados; qualquer outra
      chave: ``AttributeError(f"Report não tem o atributo {nome!r}")`` (verifique antes de copiar)."""

    def __init__(self, title: str, sections: list):
        raise NotImplementedError

    def render(self) -> str:
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError

    def __deepcopy__(self, memo):
        raise NotImplementedError

    def with_changes(self, **changes):
        raise NotImplementedError
