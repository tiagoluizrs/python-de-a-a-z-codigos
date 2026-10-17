"""Exercício 6: registrar requisições sem vazar segredos (Capítulos 3 e 12 do Volume 3)."""

SENSITIVE_HEADERS = {"authorization", "proxy-authorization", "cookie", "set-cookie", "x-api-key"}
SENSITIVE_PARAMS = {"token", "api_key", "apikey", "password", "secret", "access_token"}


def redact_url(url):
    """Devolve a URL (``str``) com o VALOR dos parâmetros de ``SENSITIVE_PARAMS`` trocado por ``***`` (sem diferenciar
    maiúsculas no nome do parâmetro). Parâmetros e ordem restantes ficam como estão; também remova ``user:senha@`` do
    endereço (``https://u:p@host`` -> ``https://***@host``)."""
    raise NotImplementedError


def redact_headers(headers):
    """Devolve um ``dict`` com os cabeçalhos, nomes em minúsculas, e o valor de ``SENSITIVE_HEADERS`` trocado por ``***``."""
    raise NotImplementedError


class RequestLog:
    """Guarda um registro por resposta, para usar como ``event_hooks={"response": [log.hook]}``.

    * ``hook(response)``: acrescenta a ``self.records`` um dicionário com ``method``, ``url`` (já passada por ``redact_url``),
      ``status``, ``headers`` (``redact_headers`` dos cabeçalhos da REQUISIÇÃO) e ``ms`` (``response.elapsed`` em ms; ``0.0`` se
      indisponível);
    * ``errors()`` devolve só os registros com status >= 400."""

    def __init__(self):
        self.records = []

    def hook(self, response):
        raise NotImplementedError

    def errors(self):
        raise NotImplementedError
