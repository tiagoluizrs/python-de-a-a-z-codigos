"""Exercício 4: um cliente de API com autenticação, erros próprios e respostas tipadas."""
import httpx  # noqa: F401


class ApiError(Exception):
    """Erro da API: ``status`` (int ou ``None`` se foi falha de rede), ``message`` e ``body`` (JSON ou texto)."""

    def __init__(self, status, message, body=None):
        super().__init__(f"{status}: {message}" if status else message)
        self.status, self.message, self.body = status, message, body


class TokenAuth(httpx.Auth):
    """``TokenAuth(token, refresh=None)``: envia ``Authorization: Bearer <token>``; se a resposta for 401 e houver
    ``refresh`` (callable sem argumentos que devolve o token novo), troca o token e repete a requisição UMA vez
    (se a segunda também for 401, a resposta 401 segue para quem chamou)."""

    def __init__(self, token, refresh=None):
        raise NotImplementedError


class ApiClient:
    """``ApiClient(base_url, token, *, refresh=None, transport=None, timeout=5.0)``.

    * usa UM ``httpx.Client`` com ``base_url``, ``TokenAuth``, ``timeout`` e ``transport`` (para testes);
    * ``get(path, **params)``, ``post(path, payload)`` e ``delete(path)``: devolvem o JSON decodificado
      (``None`` para 204 ou corpo vazio);
    * status 4xx/5xx viram ``ApiError(status, mensagem, corpo)`` (a mensagem vem de ``error`` ou ``message`` do JSON,
      senão do texto, senão ``"HTTP <status>"``); falhas de rede (``httpx.RequestError``) viram
      ``ApiError(None, ...)``; corpo que não é JSON em resposta de sucesso vira ``ApiError(status, "resposta não é JSON")``;
    * funciona como gerenciador de contexto e tem ``close()``."""

    def __init__(self, base_url, token, *, refresh=None, transport=None, timeout=5.0):
        raise NotImplementedError
