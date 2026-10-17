"""Playwright assíncrono: várias páginas ao mesmo tempo, com um limite."""
import asyncio
import time

from playwright.async_api import async_playwright

import demo_site

server, BASE = demo_site.start()
URLS = [f"{BASE}/slow?ms=300&i={i}" for i in range(12)]


async def visit(context, url, sem):
    async with sem:
        page = await context.new_page()
        try:
            await page.goto(url)
            return await page.inner_text("body")
        finally:
            await page.close()


async def run(limit: int) -> tuple[float, list[str]]:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        sem = asyncio.Semaphore(limit)
        start = time.perf_counter()
        results = await asyncio.gather(*(visit(context, u, sem) for u in URLS))
        elapsed = (time.perf_counter() - start) * 1e3
        await browser.close()
        return elapsed, results


async def main():
    print("12 páginas que demoram 300 ms cada (num mesmo navegador, páginas diferentes):")
    for limit in (1, 4, 12):
        ms, results = await run(limit)
        print(f"  {limit:>2} páginas abertas ao mesmo tempo: {ms:6.0f} ms | todas ok? {set(results) == {'devagar'}}")

    # a mesma ideia com UMA página que espera por várias coisas
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(BASE + "/spa")
        first, button = await asyncio.gather(page.wait_for_selector("article.product"), page.wait_for_selector("#more"))
        print("\nwait_for_selector em paralelo:", await first.inner_text(), "| botão:", await button.inner_text())
        await browser.close()


asyncio.run(main())
print("\n(o gargalo do navegador é a memória e a CPU: cada página aberta é um renderizador; 4 a 8 em paralelo costuma ser o ponto bom)")
server.shutdown()
