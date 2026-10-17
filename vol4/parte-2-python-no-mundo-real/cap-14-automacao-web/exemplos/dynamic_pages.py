"""Páginas dinâmicas: o HTML que o servidor manda NÃO é o que o navegador mostra. Duas saídas e o custo de cada uma."""
import time

import httpx
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

import demo_site

server, BASE = demo_site.start()


def best(fn, repeat=3):
    out = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        out.append((time.perf_counter() - start) * 1e3)
    return min(out)


# 1. o sintoma: o seletor "certo" não acha nada
html = httpx.get(BASE + "/spa").text
soup = BeautifulSoup(html, "lxml")
print(f"HTML recebido ({len(html)} bytes): produtos achados = {len(soup.select('article.product'))} | tem <script>? {'fetch(' in html}")
print("   trecho:", soup.select_one("#list"), "(vazio: os produtos são criados por JavaScript depois)")

# 2. SAÍDA A (a melhor): achar a API que o JavaScript chama e usá-la direto. Aqui sabemos: /api/products?page=N
start = time.perf_counter()
items, page = [], 1
with httpx.Client(base_url=BASE) as client:
    while True:
        data = client.get("/api/products", params={"page": page}).json()
        items += data["items"]
        if not data["has_more"]:
            break
        page += 1
t_api = (time.perf_counter() - start) * 1e3
print(f"\nA) API JSON: {len(items)} produtos em {page} chamadas, {t_api:.0f} ms | já vem tipado: {items[0]}")

# 3. como descobrir a API: observar as requisições da página (o que a aba 'Rede' do navegador mostra)
with sync_playwright() as p:
    browser = p.chromium.launch()
    page_ = browser.new_page()
    calls = []
    page_.on("request", lambda r: calls.append((r.method, r.resource_type, r.url.replace(BASE, ""))))
    page_.goto(BASE + "/spa")
    page_.wait_for_selector("article.product")
    print("\nrequisições que o navegador fez para montar a página:")
    for call in calls:
        print("  ", call)
    browser.close()

# 4. SAÍDA B: deixar um navegador de verdade executar o JavaScript e ler o resultado
def render_with_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE + "/spa")
        results = []
        while True:
            page.wait_for_selector("article.product")
            if page.locator("#more").count() == 0:
                break
            before = page.locator("article.product").count()
            page.click("#more")
            page.wait_for_function(f"document.querySelectorAll('article.product').length > {before}")
        results = page.locator("article.product .name").all_inner_texts()
        browser.close()
        return results


start = time.perf_counter()
names = render_with_browser()
t_browser = (time.perf_counter() - start) * 1e3
print(f"\nB) navegador (Playwright + Chromium): {len(names)} produtos em {t_browser:.0f} ms | primeiro: {names[0]!r}")
print(f"   mesmos nomes da API? {names == [i['name'] for i in items]}")
print(f"   o navegador custou {t_browser / t_api:.0f}x o tempo da API (e a API entrega números, não texto formatado)")

# 5. quando o navegador é a ÚNICA saída
print("""
quando usar o navegador mesmo:
  - a API exige assinatura calculada por JavaScript, token efêmero ou cookie de um fluxo de login;
  - o conteúdo vem de WebSocket/canvas/renderização complexa;
  - você precisa clicar, preencher formulários e baixar arquivos como uma pessoa;
  - o objetivo é TESTAR a interface (e aí o Playwright é a ferramenta certa, e não um raspador).""")
server.shutdown()
