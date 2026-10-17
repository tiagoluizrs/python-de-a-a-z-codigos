"""Exercício 5: download em fluxo, com progresso e retomada."""


def download(client, url, dest, *, chunk_size=65_536, on_progress=None, resume=True):
    """Baixa ``url`` para o arquivo ``dest`` (``pathlib.Path``) usando ``client.stream``.

    * ``on_progress(baixados, total)`` é chamado a cada pedaço (``total`` vem de ``Content-Length`` ou ``Content-Range``;
      ``None`` se desconhecido); ``baixados`` conta TAMBÉM os bytes que já estavam no arquivo;
    * ``resume=True`` e ``dest`` já existe com ``N`` bytes: envie ``Range: bytes=N-``; se o servidor responder
      ``206``, ACRESCENTE ao arquivo; se responder ``200`` (não suporta Range), REESCREVA do zero; se responder
      ``416`` (já está completo), não baixe nada;
    * outros status de erro levantam ``httpx.HTTPStatusError`` SEM tocar no arquivo existente;
    * devolve o tamanho final do arquivo em bytes."""
    raise NotImplementedError
