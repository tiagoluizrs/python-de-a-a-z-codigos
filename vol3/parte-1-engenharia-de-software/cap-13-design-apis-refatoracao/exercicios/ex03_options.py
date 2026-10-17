"""Exercício 3: trocar muitos parâmetros por um objeto de opções."""


# A função original (para referência): 8 parâmetros soltos
def request_legacy(url, method="GET", timeout=10.0, retries=3, verify=True, headers=None, proxy=None, follow=True):
    return (url, method, timeout, retries, verify, tuple((headers or {}).items()), proxy, follow)


class Options:
    """Objeto de valor IMUTÁVEL (``dataclass(frozen=True)``) com os campos
    ``method="GET"``, ``timeout=10.0``, ``retries=3``, ``verify=True``,
    ``headers=()`` (tupla de pares), ``proxy=None``, ``follow=True``.

    * validação em ``__post_init__``: ``timeout > 0``, ``retries >= 0``,
      ``method`` em maiúsculas dentre GET/POST/PUT/DELETE/PATCH/HEAD
      (normalize para maiúsculas); senão ``ValueError`` citando o campo;
    * ``with_(**changes)``: devolve uma NOVA ``Options`` com as mudanças; campo
      desconhecido levanta ``TypeError(f"opção desconhecida: {nome!r}")``;
    * ``from_legacy(**kwargs)`` (classmethod): aceita os nomes da função legada
      (``headers`` como ``dict``) e devolve ``Options``."""


def request(url, *, options=None, **overrides):
    """Devolve ``(url, options_finais)``: ``options`` (ou as padrão) com
    ``overrides`` aplicados via ``with_``. Mesmas validações."""
    raise NotImplementedError
