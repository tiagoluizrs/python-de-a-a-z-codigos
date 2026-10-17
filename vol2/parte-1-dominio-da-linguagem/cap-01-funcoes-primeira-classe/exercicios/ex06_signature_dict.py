"""Exercício 6: extrair a assinatura de uma função em um dict."""


def signature_dict(func):
    """Descreva ``func`` com ``inspect.signature``.

    Devolva::

        {
          "params": [
            {"name": "a", "kind": "POSITIONAL_OR_KEYWORD",
             "required": True, "default": None, "annotation": "int"},
            ...
          ],
          "returns": "str",      # ou None
        }

    * ``kind`` é o nome do kind do parâmetro;
    * ``required`` é True se o parâmetro precisa ser informado
      (sem padrão e que não seja ``*args``/``**kwargs``);
    * ``default`` é o valor padrão, ou None se não houver;
    * ``annotation`` é o ``__name__`` quando a anotação é uma classe,
      ``str(anotação)`` caso contrário, e None se não houver;
    * ``returns`` segue a mesma regra para o retorno.

    Se ``func`` não tiver assinatura disponível (como ``max``),
    devolva ``None``.
    """
    raise NotImplementedError
