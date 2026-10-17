"""Exercício 2: transformar ValidationError em algo que um usuário entende."""


def errors_to_dict(error):
    """``error`` é uma ``pydantic.ValidationError``. Devolve ``{caminho: [mensagens]}``:

    * o caminho junta o ``loc`` com pontos (``"address.zip_code"``); índices de lista entram como números
      (``"items.1.qty"``); erro sem ``loc`` (erro do modelo inteiro) usa a chave ``"__root__"``;
    * a mensagem é a de ``msg``; para erros com ``type == "value_error"`` remova o prefixo ``"Value error, "``;
    * vários erros no mesmo campo viram várias mensagens, na ordem em que aparecem."""
    raise NotImplementedError


def first_message(error):
    """Uma frase para mostrar ao usuário: ``"<caminho>: <mensagem>"`` do PRIMEIRO erro (mesmas regras de caminho e de
    prefixo); se houver mais erros, acrescente `` (+N erros)`` (``N`` = quantos faltam, com ``erro`` no singular
    quando for 1: `` (+1 erro)``)."""
    raise NotImplementedError
