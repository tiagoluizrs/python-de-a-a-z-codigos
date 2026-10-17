"""Exercício 1: um verificador de Dockerfile (as armadilhas do capítulo, em regras)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    rule: str        # "DL001"...
    line: int        # número da linha (1-based) onde a instrução COMEÇA
    message: str


def lint(dockerfile: str) -> list[Finding]:
    """Analisa o texto de um Dockerfile e devolve os achados ordenados por ``(line, rule)``.

    Antes de aplicar as regras, junte linhas continuadas com ``\\`` no fim (a instrução inteira conta como UMA, na linha
    onde começa), ignore linhas vazias e comentários (``#``) e leia a instrução (a primeira palavra, sem diferenciar
    maiúsculas de minúsculas) e o argumento (o resto).

    Regras:

    * ``DL001`` ``FROM`` sem tag ou com ``:latest`` (ignore ``FROM scratch`` e referências a etapas anteriores, como
      ``FROM builder``; uma imagem com ``@sha256:`` conta como fixada);
    * ``DL002`` o Dockerfile NÃO tem nenhuma instrução ``USER`` (o processo roda como root); reporte na linha do último
      ``FROM``;
    * ``DL003`` ``CMD`` ou ``ENTRYPOINT`` na forma shell (o argumento NÃO começa com ``[``): o PID 1 vira um ``sh`` que não
      repassa sinais;
    * ``DL004`` ``COPY . .`` (ou ``COPY . /algum/lugar``) que aparece ANTES de uma instrução ``RUN`` com ``pip install``,
      ``uv sync``, ``npm install``, ``poetry install`` ou ``apt-get install``: qualquer mudança de código invalida o cache
      da instalação (reporte uma vez, na linha do ``COPY``);
    * ``DL005`` ``pip install`` sem ``--no-cache-dir`` (e sem ``--mount=type=cache`` na mesma instrução);
    * ``DL006`` ``apt-get install`` sem ``--no-install-recommends`` ou sem ``rm -rf /var/lib/apt/lists`` na mesma instrução;
    * ``DL007`` ``ADD`` com uma origem local (use ``COPY``); não reporte ``ADD`` de URL (``http://``/``https://``);
    * ``DL008`` ``ENV`` ou ``ARG`` cujo NOME contenha ``PASSWORD``, ``SECRET``, ``TOKEN`` ou ``KEY`` (sem diferenciar
      maiúsculas de minúsculas): segredo gravado na imagem;
    * ``DL009`` não existe ``HEALTHCHECK`` (reporte na linha do último ``FROM``).

    Um Dockerfile sem nenhum ``FROM`` devolve a lista vazia."""
    raise NotImplementedError
