"""O Client reaproveita conexões: medir a diferença."""
import statistics
import time

import httpx
import requests

from demo_server import serve

N = 300


def timed(label, func):
    start = time.perf_counter()
    func()
    elapsed = time.perf_counter() - start
    print(f"  {label:<48}{elapsed * 1e3:8.0f} ms | {elapsed / N * 1e3:6.2f} ms por requisição")
    return elapsed


with serve() as base:
    url = f"{base}/json"
    print(f"{N} requisições GET ao servidor local:")
    slow = timed("httpx.get() (uma conexão nova a cada vez)", lambda: [httpx.get(url) for _ in range(N)])

    def with_client():
        with httpx.Client() as client:
            for _ in range(N):
                client.get(url)

    fast = timed("httpx.Client() reaproveitado (keep-alive)", with_client)
    timed("requests.get() (sem sessão)", lambda: [requests.get(url) for _ in range(N)])

    def with_session():
        with requests.Session() as session:
            for _ in range(N):
                session.get(url)

    timed("requests.Session()", with_session)
    print(f"  Client reaproveitado foi {slow / fast:.1f}x mais rápido que httpx.get() em laço")

    # configuração que vale para TODAS as requisições do Client
    with httpx.Client(base_url=base, headers={"User-Agent": "livro-python/1.0"}, timeout=httpx.Timeout(5.0, connect=2.0),
                      limits=httpx.Limits(max_connections=20, max_keepalive_connections=10)) as client:
        echo = client.get("/echo").json()
        print("\nClient com base_url, cabeçalho padrão e limites: user-agent recebido =", echo["headers"]["user-agent"], "| url relativa: /echo")
        print("cookies persistem no Client:", end=" ")
        client.get("/cookie")
        print(dict(client.cookies))

    # fechar: sem o with, a conexão fica aberta
    client = httpx.Client()
    client.get(url)
    print("\nclient.is_closed antes/depois de close():", client.is_closed, end=" -> ")
    client.close()
    print(client.is_closed, "(sempre use with)")
