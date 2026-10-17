"""Timeouts (o padrão é 5 s!) e novas tentativas com cuidado."""
import random
import time

import httpx

from demo_server import serve

with serve() as base:
    print("1) timeouts: o httpx tem 5 segundos por padrão, em quatro fases:", httpx.Timeout(5.0))
    with httpx.Client(base_url=base) as client:
        try:
            client.get("/slow", params={"d": 1.0}, timeout=0.3)
        except httpx.ReadTimeout as error:
            print("   /slow?d=1 com timeout=0.3 ->", type(error).__name__, "(o servidor demorou para RESPONDER)")
        try:
            httpx.get("http://10.255.255.1/", timeout=httpx.Timeout(1.0, connect=0.3))
        except (httpx.ConnectTimeout, httpx.ConnectError) as error:
            print("   endereço sem resposta, connect=0.3 ->", type(error).__name__)
        print("   timeout=None desliga TODOS os prazos: uma requisição pode esperar para sempre. Nunca em produção.")

    print("\n2) retries de TRANSPORTE só cobrem falhas de CONEXÃO:")
    transport = httpx.HTTPTransport(retries=3)
    with httpx.Client(transport=transport, base_url=base) as client:
        print("   HTTPTransport(retries=3) repete ConnectError/ConnectTimeout, NUNCA repete um 503:", client.get("/flaky", params={"key": "t", "fail": 1}).status_code)

    print("\n3) repetição de STATUS (503/429/5xx) é com você, com espera crescente e jitter:")

    def get_with_retry(client, url, attempts=5, base_delay=0.05, **kwargs):
        for attempt in range(1, attempts + 1):
            try:
                response = client.get(url, **kwargs)
                if response.status_code not in (429, 502, 503, 504):
                    return response, attempt
                wait = float(response.headers.get("Retry-After", base_delay * 2 ** (attempt - 1)))
            except (httpx.ConnectError, httpx.ReadTimeout):
                wait = base_delay * 2 ** (attempt - 1)
            if attempt == attempts:
                raise RuntimeError(f"esgotou {attempts} tentativas")
            time.sleep(wait * (0.5 + random.random() / 2))        # jitter: evita que todos os clientes repitam juntos
        raise AssertionError

    with httpx.Client(base_url=base) as client:
        start = time.perf_counter()
        response, attempts = get_with_retry(client, "/flaky", params={"key": "retry", "fail": 3})
        print(f"   /flaky falhou 3 vezes e passou na tentativa {attempts}: {response.status_code} em {(time.perf_counter() - start) * 1e3:.0f} ms")
        start = time.perf_counter()
        response, attempts = get_with_retry(client, "/ratelimit", params={"key": "rl", "after": "1"})
        print(f"   429 com Retry-After: 1 -> o cliente esperou o que o servidor pediu: {attempts} tentativas, {time.perf_counter() - start:.2f} s")

    print("\n4) cuidado: só repita o que é IDEMPOTENTE (GET, PUT, DELETE). Repetir um POST pode criar dois pedidos:")
    with httpx.Client(base_url=base) as client:
        first = client.post("/items", json={"order": 1})
        second = client.post("/items", json={"order": 1})
        print("   dois POST iguais ->", first.json()["id"], second.json()["id"], "(o servidor não sabe que é o mesmo pedido: use uma Idempotency-Key)")
