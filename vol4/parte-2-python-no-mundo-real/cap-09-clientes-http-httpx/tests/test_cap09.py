import asyncio
import pathlib

import httpx
import pytest


def mock_client(handler, **kwargs):
    return httpx.Client(transport=httpx.MockTransport(handler), base_url="http://api.test", **kwargs)


# ---------- servidor de demonstração (integração real) ----------
def test_demo_server_and_real_client(server):
    with httpx.Client(base_url=server) as client:
        assert client.get("/json").json()["items"] == [1, 2, 3]
        assert client.get("/status/404").status_code == 404
        assert client.get("/redirect/2").status_code == 302
        assert client.get("/redirect/2", follow_redirects=True).status_code == 200


# ---------- ex01 ----------
def test_retry_recovers_with_backoff(load_exercise):
    retry = load_exercise("ex01_retry").request_with_retry
    calls, sleeps = [], []

    def handler(request):
        calls.append(1)
        return httpx.Response(503) if len(calls) < 3 else httpx.Response(200, json={"ok": True})

    with mock_client(handler) as client:
        response = retry(client, "GET", "/x", retries=3, backoff=0.1, sleep=sleeps.append)
    assert response.status_code == 200 and len(calls) == 3 and sleeps == [0.1, 0.2]


def test_retry_honors_retry_after_and_returns_last_response(load_exercise):
    retry = load_exercise("ex01_retry").request_with_retry
    sleeps = []

    def handler(request):
        return httpx.Response(429, headers={"Retry-After": "2.5"})

    with mock_client(handler) as client:
        response = retry(client, "GET", "/x", retries=2, sleep=sleeps.append)
    assert response.status_code == 429 and sleeps == [2.5, 2.5]                       # nunca espera depois da última


def test_retry_only_idempotent_and_network_errors(load_exercise):
    retry = load_exercise("ex01_retry").request_with_retry
    posts, sleeps = [], []

    def handler(request):
        posts.append(request.method)
        return httpx.Response(503)

    with mock_client(handler) as client:
        assert retry(client, "POST", "/x", retries=5, sleep=sleeps.append, json={}).status_code == 503
    assert posts == ["POST"] and sleeps == []                                          # POST não é repetido

    attempts = []

    def flaky(request):
        attempts.append(1)
        if len(attempts) < 3:
            raise httpx.ConnectError("caiu", request=request)
        return httpx.Response(200)

    with mock_client(flaky) as client:
        assert retry(client, "PUT", "/x", retries=3, sleep=lambda s: None).status_code == 200 and len(attempts) == 3

    def always_down(request):
        raise httpx.ReadTimeout("lento", request=request)

    with mock_client(always_down) as client:
        with pytest.raises(httpx.ReadTimeout):
            retry(client, "GET", "/x", retries=2, sleep=lambda s: None)
        with pytest.raises(ValueError):
            retry(client, "GET", "/x", retries=-1)


# ---------- ex02 ----------
def pages_handler(request):
    page = int(request.url.params["page"])
    return httpx.Response(200, json={"items": [f"i{page}a", f"i{page}b"], "next": page + 1 if page < 3 else None})


def test_paginate_lazy_and_complete(load_exercise):
    paginate = load_exercise("ex02_pagination").paginate
    seen = []

    def handler(request):
        seen.append(int(request.url.params["page"]))
        return pages_handler(request)

    params = {"q": "x"}
    with mock_client(handler) as client:
        assert list(paginate(client, "/list", params)) == ["i1a", "i1b", "i2a", "i2b", "i3a", "i3b"]
        assert params == {"q": "x"}
        seen.clear()
        generator = paginate(client, "/list")
        assert next(generator) == "i1a" and seen == [1]                               # preguiçoso: só pediu a 1ª página
        assert list(paginate(client, "/list", max_pages=2)) == ["i1a", "i1b", "i2a", "i2b"]
        assert list(paginate(client, "/list", start=3)) == ["i3a", "i3b"]


def test_paginate_errors_and_custom_keys(load_exercise):
    paginate = load_exercise("ex02_pagination").paginate

    def handler(request):
        if request.url.path == "/bad":
            return httpx.Response(500)
        return httpx.Response(200, json={"data": [1], "more": None})

    with mock_client(handler) as client:
        with pytest.raises(httpx.HTTPStatusError):
            list(paginate(client, "/bad"))
        assert list(paginate(client, "/ok", items_key="data", next_key="more", page_param="p")) == [1]


def test_apaginate(load_exercise):
    apaginate = load_exercise("ex02_pagination").apaginate

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(pages_handler), base_url="http://api.test") as client:
            return [item async for item in apaginate(client, "/list", max_pages=2)]

    assert asyncio.run(run()) == ["i1a", "i1b", "i2a", "i2b"]


# ---------- ex03 ----------
def test_fetch_all_order_and_errors(load_exercise):
    fetch_all = load_exercise("ex03_fetch_all").fetch_all

    def handler(request):
        if request.url.path == "/down":
            raise httpx.ConnectError("sem conexão", request=request)
        if request.url.path == "/500":
            return httpx.Response(500)
        return httpx.Response(200, json={"path": request.url.path})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://api.test") as client:
            return await fetch_all(client, ["/a", "/down", "/500", "/b"], concurrency=2)

    results = asyncio.run(run())
    assert isinstance(results[0], httpx.Response) and results[0].json() == {"path": "/a"}
    assert isinstance(results[1], httpx.ConnectError)
    assert results[2].status_code == 500 and results[3].json() == {"path": "/b"}


def test_fetch_all_limits_concurrency(load_exercise):
    fetch_all = load_exercise("ex03_fetch_all").fetch_all
    state = {"now": 0, "peak": 0}

    async def handler(request):
        state["now"] += 1
        state["peak"] = max(state["peak"], state["now"])
        await asyncio.sleep(0.02)
        state["now"] -= 1
        return httpx.Response(200)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://api.test") as client:
            return await fetch_all(client, [f"/{i}" for i in range(30)], concurrency=4)

    assert len(asyncio.run(run())) == 30 and state["peak"] == 4
    async def empty():
        async with httpx.AsyncClient() as client:
            return await fetch_all(client, [])
    assert asyncio.run(empty()) == []
    with pytest.raises(ValueError):
        asyncio.run(load_exercise("ex03_fetch_all").fetch_all(None, ["/x"], concurrency=0))


# ---------- ex04 ----------
def test_api_client_happy_path_and_auth(load_exercise):
    m = load_exercise("ex04_api_client")
    seen = []

    def handler(request):
        seen.append((request.method, request.url.path, request.headers.get("authorization")))
        if request.method == "POST":
            return httpx.Response(201, json={"id": 7, **__import__("json").loads(request.content)})
        if request.method == "DELETE":
            return httpx.Response(204)
        return httpx.Response(200, json={"echo": dict(request.url.params)})

    with m.ApiClient("http://api.test", "tok", transport=httpx.MockTransport(handler)) as api:
        assert api.get("/things", page="2", q="x") == {"echo": {"page": "2", "q": "x"}}
        assert api.post("/things", {"name": "a"}) == {"id": 7, "name": "a"}
        assert api.delete("/things/7") is None
    assert all(auth == "Bearer tok" for _, _, auth in seen)


def test_api_client_refreshes_token_once(load_exercise):
    m = load_exercise("ex04_api_client")
    tokens, refreshed = [], []

    def handler(request):
        token = request.headers["authorization"]
        tokens.append(token)
        return httpx.Response(200, json={"ok": True}) if token == "Bearer novo" else httpx.Response(401, json={"error": "expirado"})

    transport = httpx.MockTransport(handler)
    with m.ApiClient("http://api.test", "velho", refresh=lambda: refreshed.append(1) or "novo", transport=transport) as api:
        assert api.get("/x") == {"ok": True} and tokens == ["Bearer velho", "Bearer novo"] and len(refreshed) == 1
        assert api.get("/y") == {"ok": True} and len(refreshed) == 1                      # o token novo foi guardado

    with m.ApiClient("http://api.test", "ruim", refresh=lambda: "tambem-ruim", transport=transport) as api:
        with pytest.raises(m.ApiError) as info:
            api.get("/x")
    assert info.value.status == 401 and info.value.message == "expirado"


def test_api_client_error_translation(load_exercise):
    m = load_exercise("ex04_api_client")

    def handler(request):
        path = request.url.path
        if path == "/json-error":
            return httpx.Response(422, json={"message": "campo inválido", "field": "x"})
        if path == "/text-error":
            return httpx.Response(502, text="gateway ruim")
        if path == "/empty-error":
            return httpx.Response(500)
        if path == "/not-json":
            return httpx.Response(200, text="<html>")
        if path == "/network":
            raise httpx.ConnectError("sem rede", request=request)
        return httpx.Response(200, json=[1])

    with m.ApiClient("http://api.test", "t", transport=httpx.MockTransport(handler)) as api:
        for path, status, message in (("/json-error", 422, "campo inválido"), ("/text-error", 502, "gateway ruim"), ("/empty-error", 500, "HTTP 500")):
            with pytest.raises(m.ApiError) as info:
                api.get(path)
            assert (info.value.status, info.value.message) == (status, message)
        with pytest.raises(m.ApiError, match="não é JSON"):
            api.get("/not-json")
        with pytest.raises(m.ApiError) as info:
            api.get("/network")
        assert info.value.status is None and "ConnectError" in info.value.message
        assert api.get("/ok") == [1]


# ---------- ex05 ----------
DATA = bytes(range(256)) * 40


def download_handler(request):
    if request.url.path == "/no-range":
        return httpx.Response(200, content=DATA)
    if request.url.path == "/missing":
        return httpx.Response(404)
    header = request.headers.get("range")
    if header:
        start = int(header[6:].split("-")[0])
        if start >= len(DATA):
            return httpx.Response(416)
        return httpx.Response(206, content=DATA[start:], headers={"Content-Range": f"bytes {start}-{len(DATA) - 1}/{len(DATA)}"})
    return httpx.Response(200, content=DATA)


def test_download_fresh_with_progress(load_exercise, tmp_path):
    download = load_exercise("ex05_download").download
    progress = []
    with mock_client(download_handler) as client:
        size = download(client, "/file", tmp_path / "f.bin", chunk_size=4096, on_progress=lambda d, t: progress.append((d, t)))
    assert size == len(DATA) and (tmp_path / "f.bin").read_bytes() == DATA
    assert progress[-1] == (len(DATA), len(DATA)) and [d for d, _ in progress] == sorted(d for d, _ in progress)


def test_download_resume_variants(load_exercise, tmp_path):
    download = load_exercise("ex05_download").download
    path = tmp_path / "f.bin"
    path.write_bytes(DATA[:3000])
    progress = []
    with mock_client(download_handler) as client:
        assert download(client, "/file", path, on_progress=lambda d, t: progress.append(d)) == len(DATA)
        assert path.read_bytes() == DATA and progress[0] > 3000                       # contou os bytes que já existiam
        assert download(client, "/file", path) == len(DATA) and path.read_bytes() == DATA   # 416: já completo
        path.write_bytes(b"lixo-antigo")
        assert download(client, "/no-range", path) == len(DATA) and path.read_bytes() == DATA   # 200: reescreve
        path.write_bytes(b"parcial")
        assert download(client, "/file", path, resume=False) == len(DATA)


def test_download_error_keeps_existing_file(load_exercise, tmp_path):
    download = load_exercise("ex05_download").download
    path = tmp_path / "f.bin"
    path.write_bytes(b"importante")
    with mock_client(download_handler) as client:
        with pytest.raises(httpx.HTTPStatusError):
            download(client, "/missing", path)
    assert path.read_bytes() == b"importante"


# ---------- ex06 ----------
def test_redact_url_and_headers(load_exercise):
    m = load_exercise("ex06_safe_logging")
    assert m.redact_url("https://api.test/x?page=2&Token=abc&q=oi&API_KEY=k1") == "https://api.test/x?page=2&Token=***&q=oi&API_KEY=***"
    assert m.redact_url("https://user:pw@api.test/x") == "https://***@api.test/x"
    assert m.redact_url("https://api.test/x") == "https://api.test/x" and m.redact_url("https://a.test/?password=") == "https://a.test/?password=***"
    assert m.redact_headers({"Authorization": "Bearer s", "Accept": "json", "X-Api-Key": "k", "Cookie": "a=b"}) == {
        "authorization": "***", "accept": "json", "x-api-key": "***", "cookie": "***"}


def test_request_log_hook_with_real_transport(load_exercise, server):
    m = load_exercise("ex06_safe_logging")
    log = m.RequestLog()
    with httpx.Client(base_url=server, event_hooks={"response": [log.hook]}, headers={"Authorization": "Bearer segredo"}) as client:
        client.get("/json", params={"token": "s3", "page": 1})
        client.get("/status/500")
    assert [(r["method"], r["status"]) for r in log.records] == [("GET", 200), ("GET", 500)]
    assert "s3" not in log.records[0]["url"] and "token=***" in log.records[0]["url"] and "page=1" in log.records[0]["url"]
    assert log.records[0]["headers"]["authorization"] == "***" and "segredo" not in str(log.records)
    assert [r["status"] for r in log.errors()] == [500] and log.records[0]["ms"] >= 0
