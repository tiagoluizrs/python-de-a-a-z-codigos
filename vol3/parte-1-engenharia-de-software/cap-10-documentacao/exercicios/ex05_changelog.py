"""Exercício 5: changelog no formato Keep a Changelog."""


def parse_changelog(text):
    """Interpreta um changelog:

    ```
    ## [1.2.0] - 2026-10-13
    ### Added
    - algo novo
    ### Fixed
    - correção

    ## [Unreleased]
    ### Changed
    - algo
    ```

    Devolve uma lista, na ordem do texto, de dicts ``{"version": "1.2.0",
    "date": "2026-10-13", "sections": {"Added": ["algo novo"], "Fixed": [...]}}``.
    ``"Unreleased"`` tem ``"date": None``. Itens são linhas ``- texto`` (sem o
    ``- ``). Linhas fora dessa estrutura são ignoradas."""
    raise NotImplementedError


def next_version(current, sections):
    """Versão SemVer seguinte a ``current`` (``"1.4.2"``), dado o dict de seções
    (como em ``parse_changelog``): se algum item (em qualquer seção) começar com
    ``"BREAKING"``, ou houver a seção ``Removed`` não vazia -> MAJOR
    (``"2.0.0"``); senão, se ``Added`` não vazia -> MINOR (``"1.5.0"``); senão ->
    PATCH (``"1.4.3"``). Versão inválida levanta ``ValueError``."""
    raise NotImplementedError
