"""Exercício 5: __getattr__, __setattr__ e __dir__."""


class AttrView:
    """Acesso por atributo às chaves de um dict, somente leitura.

    * ``v = AttrView({"host": "x", "port": 1})``; ``v.host == "x"``;
    * chave inexistente: ``AttributeError`` cuja mensagem cita o nome;
    * atribuir ou apagar qualquer atributo levanta ``AttributeError``;
    * ``dir(v)`` lista as chaves (ordenadas);
    * ``hasattr(v, "host")`` é verdadeiro e ``hasattr(v, "nope")`` é falso;
    * a view guarda uma CÓPIA do dict original;
    * chaves que não são identificadores (``"a-b"``) continuam acessíveis
      via ``getattr(v, "a-b")``.
    """

    def __init__(self, data):
        raise NotImplementedError
