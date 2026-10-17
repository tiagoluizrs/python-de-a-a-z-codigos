"""Exercício 1: o verificador de prontidão para produção (um subconjunto das regras do capítulo)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str              # "erro" ou "aviso"
    message: str = ""


def scan_project(files: dict[str, str]) -> list[Finding]:
    """``files`` mapeia caminho relativo (com ``/``) -> conteúdo de texto. Aplique estas regras e devolva os achados ordenados por
    ``(severity != "erro", rule)`` (erros primeiro, depois por regra; use ``sorted`` estável sobre a ordem em que os gerou):

    * ``PR001`` (erro): não há ``pyproject.toml`` OU ele não contém o texto ``requires-python``;
    * ``PR002`` (erro): nenhum arquivo ``uv.lock``, ``poetry.lock``, ``pdm.lock`` ou ``Pipfile.lock``, E nenhum arquivo cujo nome case com
      ``requirements*.txt`` e contenha ``==``;
    * ``PR003`` (erro): nenhum arquivo cujo NOME (a última parte do caminho) comece com ``test_`` e termine com ``.py``, ou termine com
      ``_test.py``;
    * ``PR006``: se existir um arquivo chamado ``.env`` (na raiz): erro; senão, se existir ``.gitignore`` e nenhuma de suas linhas
      começar com ``.env``: aviso;
    * ``PR007`` (erro): UM achado por arquivo ``.py``, ``.yaml``, ``.yml``, ``.toml``, ``.json``, ``.cfg`` ou ``.ini`` cujo conteúdo
      tenha um segredo: ``AKIA`` seguido de 16 maiúsculas/dígitos, OU uma atribuição ``password``/``senha``/``secret``/``api_key``/
      ``token`` (sem diferenciar maiúsculas; ``api-key`` e ``api_key`` valem) com ``=`` e um valor entre aspas com 6 ou mais caracteres sem
      espaços (``token = "abc123xyz"``), OU um cabeçalho ``-----BEGIN PRIVATE KEY-----`` (também ``RSA``/``EC``/``OPENSSH``);
    * ``message`` pode ser qualquer texto útil (os testes só conferem ``rule`` e ``severity``)."""
    raise NotImplementedError


def scan_dockerfile(text: str) -> list[Finding]:
    """Analisa um Dockerfile (linhas em branco e comentários ignorados; instruções sem diferenciar maiúsculas):

    * ``PR004`` (erro): nenhuma instrução ``USER``;
    * ``PR004`` (aviso): nenhuma instrução ``HEALTHCHECK``;
    * ``PR004`` (erro): um ``FROM`` cuja imagem não tem tag nem resumo (``python``) ou usa ``:latest`` (ignore ``scratch`` e os nomes de
      etapas anteriores, definidos com ``FROM x AS nome``); um achado por ``FROM`` problemático;
    * ``PR004`` (erro): um ``ENV`` ou ``ARG`` cujo nome (até o ``=`` ou o espaço) contenha ``PASSWORD``, ``SECRET``, ``TOKEN`` ou ``KEY``
      (sem diferenciar maiúsculas); um achado por linha.
    Devolva os achados na ordem em que foram gerados (erros e avisos misturados): na ordem ``USER``, ``HEALTHCHECK``, depois os ``FROM`` e os
    ``ENV``/``ARG`` na ordem das linhas."""
    raise NotImplementedError


def score(findings: list[Finding]) -> int:
    """100 menos 15 por erro e 5 por aviso, nunca abaixo de 0."""
    raise NotImplementedError


def render(findings: list[Finding]) -> str:
    """Um texto para o terminal: uma linha ``[erro ] PR001 mensagem`` por achado (a severidade alinhada à esquerda em 5 colunas, dentro
    dos colchetes: ``"[erro ]"`` e ``"[aviso]"``) e, no fim, a linha ``placar: N/100 (E erros, A avisos)``. Sem achados, só a linha do placar
    (com ``100/100 (0 erros, 0 avisos)``)."""
    raise NotImplementedError
