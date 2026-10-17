"""Exercício 1: o Singleton clássico por ``__new__``, sem as armadilhas da versão ingênua."""


class Config:
    """Uma configuração única por classe.

    * ``Config()`` devolve SEMPRE a mesma instância; ``Config(values)`` (um dict) usa ``values`` (copiado) só na PRIMEIRA criação;
    * depois de criada, chamar ``Config(values)`` com um ``values`` que não seja ``None`` levanta ``ValueError("Config já foi criada; use set()")``
      (``Config()`` sem argumentos continua permitido);
    * o estado NÃO pode ser apagado por chamadas posteriores a ``Config()`` (cuidado com o ``__init__``: ele roda a cada chamada);
    * ``get(key, default=None)`` e ``set(key, value)``;
    * cada SUBCLASSE tem a sua própria instância única: ``Sub() is Sub()`` e ``Sub() is not Config()`` (não herde o ``_instance`` do pai);
    * ``Config.created`` conta quantas instâncias foram CRIADAS de fato (uma por classe, até um ``reset_for_tests``) e é um contador da própria
      classe (``Sub.created`` não soma no ``Config.created``);
    * ``reset_for_tests()`` (``classmethod``) descarta a instância da classe: a próxima chamada cria outra, com a lista de valores nova."""

    created = 0

    def get(self, key, default=None):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError

    @classmethod
    def reset_for_tests(cls):
        raise NotImplementedError
