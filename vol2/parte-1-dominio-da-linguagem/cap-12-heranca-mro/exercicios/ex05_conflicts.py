"""Exercício 5: onde o MRO tem conflitos de nomes."""


def find_overrides(cls):
    """Para cada método definido em MAIS DE UMA classe do MRO de ``cls``
    (ignorando ``object`` e nomes que começam com ``__``), devolva um dict
    ``{nome: [nomes das classes que o definem, na ordem do MRO]}``.

    Use ``vars(klass)`` (o dicionário da própria classe, sem herança) e
    considere só os atributos ``callable`` (funções, não dados).
    """
    raise NotImplementedError
