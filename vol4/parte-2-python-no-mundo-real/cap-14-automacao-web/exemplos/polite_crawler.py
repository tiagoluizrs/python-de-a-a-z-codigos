"""Raspar com educação: robots.txt, identificação, limite de ritmo, tentativas, cache condicional e concorrência."""
import asyncio
import time
from urllib import robotparser

import httpx

import demo_site

server, BASE = demo_site.start()
UA = "curso-python-bot/1.0 (+contato@exemplo.com)"

# 1. robots.txt: o site diz o que NÃO quer que você leia (e o ritmo)
robots = robotparser.RobotFileParser()
robots.parse(httpx.get(BASE + "/robots.txt").text.splitlines())
for path in ("/catalog", "/product/3", "/admin", "/account"):
    print(f"  pode ler {path:<12}? {robots.can_fetch(UA, BASE + path)}")
print("Crawl-delay para o nosso User-Agent:", robots.crawl_delay(UA), "s | badbot pode ler /catalog?", robots.can_fetch("badbot", BASE + "/catalog"))
print("(robots.txt é um PEDIDO de boa educação, não uma barreira técnica; ignorá-lo é a diferença entre ser bem-vindo e ser banido)")

# 2. identificar-se: um User-Agent com nome e contato
print("\nsem identificação:", httpx.get(BASE + "/ua-only").status_code, "| identificado:", httpx.get(BASE + "/ua-only", headers={"User-Agent": UA}).status_code)


# 3. tentar de novo com espera crescente e RESPEITAR o Retry-After
def fetch_with_retry(client: httpx.Client, url: str, retries: int = 4, sleep=time.sleep):
    waits = []
    for attempt in range(retries + 1):
        response = client.get(url)
        if response.status_code not in (429, 500, 502, 503, 504):
            return response, waits
        retry_after = response.headers.get("Retry-After")
        wait = float(retry_after) if retry_after else min(0.1 * 2 ** attempt, 2.0)          # backoff exponencial limitado
        waits.append(wait)
        sleep(wait)
    raise RuntimeError(f"desistindo de {url} após {retries + 1} tentativas")


with httpx.Client(base_url=BASE, headers={"User-Agent": UA, "X-Client": "teste-retry"}) as client:
    response, waits = fetch_with_retry(client, "/flaky")
    print(f"\n/flaky -> {response.status_code} {response.text!r} após esperas de {waits} (503 duas vezes)")
    start = time.perf_counter()
    response, waits = fetch_with_retry(client, "/limited")
    print(f"/limited -> {response.status_code} esperas {waits} (obedeceu o Retry-After: 1 s) em {time.perf_counter() - start:.1f} s")

# 4. requisição condicional: não baixar de novo o que não mudou (ETag e If-None-Match)
with httpx.Client(base_url=BASE, headers={"User-Agent": UA}) as client:
    first = client.get("/etag")
    again = client.get("/etag", headers={"If-None-Match": first.headers["ETag"]})
    print(f"\nETag: 1ª vez {first.status_code} com {len(first.content):,} bytes | 2ª vez {again.status_code} com {len(again.content)} bytes (o servidor poupou a transferência)")


# 5. cache da resposta (aqui em memória; em disco é o mesmo raciocínio): no DESENVOLVIMENTO, baixe cada página UMA vez
class ResponseCache:
    def __init__(self, client):
        self.client, self.store, self.network_calls = client, {}, 0

    def get(self, url):
        if url not in self.store:
            self.network_calls += 1
            self.store[url] = self.client.get(url).text
        return self.store[url]


with httpx.Client(base_url=BASE, headers={"User-Agent": UA}) as client:
    cache = ResponseCache(client)
    for _ in range(50):                                              # 50 execuções do seu parser em desenvolvimento
        cache.get("/catalog?page=1")
    print(f"cache: 50 leituras da mesma página = {cache.network_calls} requisição ao servidor")

# 6. sequencial x concorrente, com um limite (semáforo) e um espaçamento entre requisições
URLS = [f"/slow?ms=200&i={i}" for i in range(20)]


def sequential():
    with httpx.Client(base_url=BASE, headers={"User-Agent": UA}) as client:
        for url in URLS:
            client.get(url)


async def concurrent(limit: int, delay: float = 0.0):
    sem = asyncio.Semaphore(limit)
    async with httpx.AsyncClient(base_url=BASE, headers={"User-Agent": UA}) as client:
        async def one(url):
            async with sem:
                response = await client.get(url)
                if delay:
                    await asyncio.sleep(delay)                      # espaçamento: cada 'vaga' só volta depois de uma pausa
                return response.status_code
        return await asyncio.gather(*(one(u) for u in URLS))


start = time.perf_counter()
sequential()
t_seq = time.perf_counter() - start
print(f"\n20 páginas de 200 ms:  sequencial {t_seq * 1e3:6.0f} ms")
for limit, delay in ((5, 0.0), (20, 0.0), (5, 0.2)):
    start = time.perf_counter()
    asyncio.run(concurrent(limit, delay))
    print(f"                       {limit:>2} em paralelo, pausa de {delay:.1f} s: {(time.perf_counter() - start) * 1e3:6.0f} ms")
print("(a concorrência derruba 4 segundos para 0,2 a 1 s, mas é ELA que derruba servidores pequenos: 20 de uma vez, contra um site pequeno, já pesa como um ataque)")
hits = httpx.get(BASE + "/hits").json()
print("o servidor contou", hits.get("/slow"), "requisições em /slow")

# 7. um 'raspador' bem-educado junta tudo: robots + identificação + limite + tentativas + cache
print("\nregras: ler o robots.txt, se identificar, ≤ 1 requisição por segundo por site (ou o Crawl-delay), tentar de novo com espera,")
print("        guardar o que baixou e NÃO baixar o que não precisa; e parar quando o site pedir (429, 403 ou um e-mail).")
server.shutdown()
