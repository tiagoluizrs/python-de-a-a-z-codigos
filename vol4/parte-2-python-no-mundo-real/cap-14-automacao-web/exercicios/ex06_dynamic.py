"""Exercício 6: automatizar uma página que o JavaScript monta (precisa do Chromium: ``uv run playwright install chromium``)."""


def load_all(page, item_selector: str, more_selector: str, timeout_ms: int = 3000) -> list[str]:
    """``page`` é uma ``playwright.sync_api.Page`` JÁ aberta. A página mostra itens (``item_selector``) e um botão
    (``more_selector``) que carrega mais itens e SOME quando acabam. Clique no botão até ele sumir e devolva o texto de
    TODOS os itens (``inner_text``), na ordem.

    Regras: nada de ``time.sleep``; espere por condições (o primeiro lote chega depois de um atraso; cada clique
    também demora). Se algum clique não trouxer item novo em ``timeout_ms``, deixe o erro do Playwright subir."""
    raise NotImplementedError


def read_table(page, table_selector: str) -> list[dict]:
    """Lê uma tabela HTML (que pode ser preenchida depois por JavaScript) como lista de dicts: as chaves vêm do texto
    de cada ``<th>`` (sem espaços nas pontas) e os valores, do texto de cada ``<td>``, linha a linha do ``<tbody>``.
    Espere a tabela ter ao menos uma linha no ``<tbody>`` (até 3 s). Tabela vazia depois da espera: levante
    ``ValueError("tabela vazia")``."""
    raise NotImplementedError


def fill_and_submit(page, values: dict[str, str]) -> None:
    """Preenche um formulário: para cada ``nome -> valor`` de ``values``, ache o campo ``[name=<nome>]`` e preencha
    (``<input>``, ``<textarea>``) ou escolha a opção (``<select>``); depois clique no botão de envio
    (``button[type=submit]``) e espere a navegação terminar (``load``)."""
    raise NotImplementedError
