"""Playwright (API síncrona): localizadores, ações, esperas automáticas, rede, estado de login e rastros."""
import tempfile
import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

import demo_site

server, BASE = demo_site.start()
OUT = Path(__file__).parent / "saida"
OUT.mkdir(exist_ok=True)

with sync_playwright() as p:
    start = time.perf_counter()
    browser = p.chromium.launch()                       # headless por padrão; launch(headless=False) mostra a janela
    print(f"navegador {browser.browser_type.name} {browser.version} iniciou em {(time.perf_counter() - start) * 1e3:.0f} ms")

    # 1. Browser > BrowserContext > Page: o contexto é um "perfil" isolado (cookies, storage), barato de criar
    context = browser.new_context(locale="pt-BR", timezone_id="America/Sao_Paulo", viewport={"width": 1000, "height": 700},
                                  user_agent="curso-python-bot/1.0 (+contato@exemplo.com)")
    page = context.new_page()
    page.goto(BASE + "/form")
    print("\ntítulo:", page.title(), "| URL:", page.url.replace(BASE, ""))

    # 2. localizadores: o jeito moderno (por papel e por texto, como um usuário enxerga), e o CSS quando precisar
    page.get_by_label("Termo").fill("monitor")                          # por rótulo do campo
    page.get_by_label("Categoria").select_option("monitores")
    page.get_by_label("só em estoque").check()
    page.get_by_role("button", name="Buscar").click()                  # por papel e nome acessível
    page.wait_for_url("**/search?*")
    print("\nbusca feita:", page.url.replace(BASE, ""))
    print("contagem:", page.locator("#count").inner_text())
    rows = page.locator("#results tbody tr")
    print("linhas:", rows.count(), "|", [row.locator("td").all_inner_texts() for row in rows.all()])

    # 3. esperas AUTOMÁTICAS: cada ação espera o elemento existir, estar visível e estável (sem sleep!)
    page.goto(BASE + "/spa")
    start = time.perf_counter()
    page.locator("article.product").first.wait_for()                    # o JavaScript cria o elemento depois de 300 ms
    print(f"\nprimeiro produto apareceu depois de {(time.perf_counter() - start) * 1e3:.0f} ms de espera automática")
    try:
        page.locator("#nao-existe").click(timeout=500)
    except PlaywrightTimeout as error:
        print("elemento ausente ->", type(error).__name__, "depois de 0,5 s:", str(error).splitlines()[0][:60])

    # 4. executar JavaScript na página e ler o resultado como dado do Python
    total = page.evaluate("() => [...document.querySelectorAll('article.product')].length")
    print("\nevaluate: produtos no DOM agora:", total, "| título via JS:", page.evaluate("document.title"))
    prices = page.eval_on_selector_all("article.product", "els => els.map(e => e.querySelector('.name').textContent)")
    print("eval_on_selector_all:", prices[:2])

    # 5. screenshot e PDF (evidência visual e testes de regressão)
    page.screenshot(path=OUT / "spa.png", full_page=True)
    print(f"\nscreenshot: {(OUT / 'spa.png').stat().st_size / 1e3:.0f} kB")

    # 6. rede: bloquear o que não precisa (imagens, fontes, anúncios) acelera e poupa banda; e simular respostas
    page2 = context.new_page()
    seen = []
    page2.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda route: route.abort())
    page2.route("**/api/products*", lambda route: route.fulfill(json={"page": 1, "items": [{"id": 99, "name": "Produto de mentira", "price": 1.0}], "has_more": False}))
    page2.on("response", lambda r: seen.append((r.status, r.url.replace(BASE, ""))))
    api_before = demo_site.HITS["/api/products"]
    page2.goto(BASE + "/spa")
    page2.locator("article.product").first.wait_for()
    print("\nresposta SIMULADA da API:", page2.locator("article.product .name").all_inner_texts(), "| chamadas reais ao servidor em /api:", demo_site.HITS["/api/products"] - api_before)
    page2.close()

    # 7. diálogos e downloads
    page.goto(BASE + "/spa")
    page.on("dialog", lambda d: (print("diálogo:", d.type, d.message), d.accept()))
    page.evaluate("alert('Olá do JavaScript')")
    page.goto(BASE + "/login")
    page.fill("#user", "ana")
    page.fill("#password", "123")
    page.get_by_role("button").click()
    page.wait_for_url("**/account")
    print("\nlogado:", page.locator("#welcome").inner_text())
    with page.expect_download() as download_info:
        page.click("#export")
    download = download_info.value
    download.save_as(OUT / download.suggested_filename)
    print("download:", download.suggested_filename, "|", (OUT / download.suggested_filename).read_text().splitlines()[:2])

    # 8. estado de login: faça o login UMA vez e reaproveite o cookie em outras execuções
    state = OUT / "state.json"
    context.storage_state(path=state)
    context.close()
    fresh = browser.new_context(storage_state=state)
    page3 = fresh.new_page()
    page3.goto(BASE + "/account")
    print("novo contexto com o estado salvo já entra logado?", page3.locator("#welcome").count() == 1, "| cookies:", [c["name"] for c in fresh.cookies()])
    anonymous = browser.new_context().new_page()
    anonymous.goto(BASE + "/account")
    print("contexto sem estado vai para:", anonymous.url.replace(BASE, ""))
    fresh.close()

    # 9. rastro: uma gravação reproduzível (DOM, rede, console) para depurar uma falha no CI
    trace_ctx = browser.new_context()
    trace_ctx.tracing.start(screenshots=True, snapshots=True)
    tp = trace_ctx.new_page()
    tp.goto(BASE + "/catalog")
    tp.get_by_role("link", name="Teclado Mecânico").click()
    trace_ctx.tracing.stop(path=OUT / "trace.zip")
    print(f"\ntrace.zip: {(OUT / 'trace.zip').stat().st_size / 1e3:.0f} kB (abra com: uv run playwright show-trace saida/trace.zip)")
    trace_ctx.close()

    # 10. quanto custa um contexto novo, comparado com subir o navegador
    start = time.perf_counter()
    for _ in range(10):
        c = browser.new_context()
        c.new_page().goto(BASE + "/")
        c.close()
    print(f"10 contextos novos (cada um com uma página): {(time.perf_counter() - start) * 1e3:.0f} ms no total")
    browser.close()
server.shutdown()
