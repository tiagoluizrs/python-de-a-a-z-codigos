"""Fazer requisições, ler respostas, tratar erros."""
import json
import urllib.request

import httpx

from demo_server import serve

print("httpx", httpx.__version__)
with serve() as base:
    # 1. o mais simples
    response = httpx.get(f"{base}/json")
    print("status:", response.status_code, "| ok:", response.is_success, "| tipo:", response.headers["content-type"])
    print("json():", response.json(), "| text:", response.text[:30], "| bytes:", response.content[:12])
    print("tempo da resposta:", f"{response.elapsed.total_seconds() * 1e3:.1f} ms", "| versão HTTP:", response.http_version)

    # 2. parâmetros, cabeçalhos e corpo JSON: o httpx monta e escapa para você
    echo = httpx.get(f"{base}/echo", params={"q": "python & café", "page": 2}, headers={"X-Request-Id": "abc"}).json()
    print("query enviada:", echo["path"], "| cabeçalho chegou:", echo["headers"]["x-request-id"])
    created = httpx.post(f"{base}/items", json={"name": "caneta", "price": 9.9})
    print("POST json=:", created.status_code, created.json())
    print("content-type enviado pelo httpx:", httpx.Request("POST", f"{base}/items", json={"a": 1}).headers["content-type"])

    # 3. status HTTP NÃO levanta exceção sozinho
    missing = httpx.get(f"{base}/status/404")
    print("\n404 não levantou nada:", missing.status_code, missing.is_client_error, "| httpx.codes.NOT_FOUND =", int(httpx.codes.NOT_FOUND))
    try:
        missing.raise_for_status()
    except httpx.HTTPStatusError as error:
        print("raise_for_status ->", type(error).__name__, "| error.response.status_code =", error.response.status_code)

    # 4. erros de REDE (antes de haver resposta) são outra hierarquia
    for label, url in (("porta fechada", "http://127.0.0.1:1/"), ("nome inexistente", "http://host.invalido.test/")):
        try:
            httpx.get(url, timeout=2)
        except httpx.RequestError as error:
            print(f"{label}: {type(error).__name__} (subclasse de httpx.RequestError: {isinstance(error, httpx.TransportError)})")

    # 5. redirecionamentos: NÃO são seguidos por padrão (diferente do requests)
    redirect = httpx.get(f"{base}/redirect/2")
    followed = httpx.get(f"{base}/redirect/2", follow_redirects=True)
    print("\nredirect sem follow_redirects:", redirect.status_code, redirect.headers["location"], "| com:", followed.status_code, "passando por", [r.status_code for r in followed.history])

    # 6. a biblioteca padrão faz o mesmo, com muito mais código
    with urllib.request.urlopen(f"{base}/json") as raw:
        print("\nurllib:", json.loads(raw.read()), "(sem timeout padrão, sem JSON, sem pool: use só em scripts mínimos)")

print("\nhierarquia: httpx.HTTPError -> RequestError (TransportError: ConnectError, ReadTimeout... | DecodingError) e HTTPStatusError (só com raise_for_status)")
