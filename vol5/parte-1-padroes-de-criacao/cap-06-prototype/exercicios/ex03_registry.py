"""Exercício 3: o registro de protótipos (o "prototype manager" do GoF), com ``copy.deepcopy``."""


class PrototypeRegistry:
    """Guarda protótipos por nome e cria cópias deles.

    * ``register(name, prototype)``: guarda uma CÓPIA PROFUNDA (alterar o original depois não afeta o protótipo guardado); nome já registrado:
      ``ValueError(f"protótipo já registrado: {name}")``; nome vazio: ``ValueError("nome vazio")``;
    * ``create(name, **changes)``: devolve uma NOVA cópia profunda do protótipo guardado e, para cada ``(atributo, valor)`` de ``changes``,
      faz ``setattr`` na cópia. Atributo que o protótipo não tem: ``AttributeError(f"{nome!r} não é um atributo de {Classe}")`` (a classe pelo
      ``__name__``; nada deve ser alterado no protótipo guardado). Nome desconhecido:
      ``KeyError(f"protótipo desconhecido: {name}; disponíveis: a, b")`` (alfabético; ``disponíveis: nenhum`` se vazio);
    * ``names()``: os nomes em ordem alfabética; ``unregister(name)`` remove (``KeyError`` se não existe);
    * ``__len__`` e ``__contains__``."""

    def register(self, name: str, prototype) -> None:
        raise NotImplementedError

    def create(self, name: str, **changes):
        raise NotImplementedError

    def names(self) -> list[str]:
        raise NotImplementedError

    def unregister(self, name: str) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __contains__(self, name: str) -> bool:
        raise NotImplementedError
