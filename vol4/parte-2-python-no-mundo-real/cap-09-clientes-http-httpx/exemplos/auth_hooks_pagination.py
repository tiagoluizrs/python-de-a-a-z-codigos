"""Autenticação, event hooks, paginação."""
import logging
import re
import time

import httpx

from demo_server import serve


class BearerAuth(httpx.Auth):
    """Fluxo de autenticação: envia o token e, se vier 401, renova UMA vez e repete."""

    def __init__(self, token, refresh):
        self.token, self.refresh = token, refresh

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        response = yield request
        if response.status_code == 401:
            self.token = self.refresh()
            request.headers["Authorization"] = f"Bearer {self.token}"
            yield request


SECRET = re.compile(r"(token|api_key|password)=[^&]+", re.IGNORECASE)
log = logging.getLogger("http")
logging.basicConfig(level=logging.INFO, format="  [log] %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)           # o httpx já registra cada requisição em INFO; aqui queremos só o nosso log


def log_response(response):                              # event hook: roda a cada resposta
    request = response.request
    elapsed = response.elapsed.total_seconds() * 1e3 if response.is_closed else 0
    log.info("%s %s -> %s", request.method, SECRET.sub(r"\1=***", str(request.url)), response.status_code)


with serve() as base:
    # 1. autenticação com renovação
    refreshes = []
    auth = BearerAuth("expirado", lambda: refreshes.append(1) or "valid")
    with httpx.Client(base_url=base, auth=auth) as client:
        response = client.get("/secure")
        print("401 -> renovou o token e repetiu:", response.status_code, response.json(), "| renovações:", len(refreshes))
        client.get("/secure")
        print("a 2ª chamada já usa o token novo: renovações continuam", len(refreshes))
    print("auth básica: httpx.BasicAuth('u', 'p') ou auth=('u', 'p'); chave de API: headers={'X-API-Key': ...}")

    # 2. event hooks: log de todas as requisições, com segredos mascarados
    print("\nevent hooks (a URL tem um segredo na query):")
    with httpx.Client(base_url=base, event_hooks={"response": [log_response]}) as client:
        client.get("/json", params={"token": "s3gr3d0", "page": 1})
        client.get("/status/404")

    # 3. paginação como gerador: o chamador não sabe que existem páginas
    def all_items(client):
        page = 1
        while page:
            data = client.get("/pages", params={"page": page}).raise_for_status().json()
            yield from data["items"]
            page = data["next"]

    with httpx.Client(base_url=base) as client:
        items = []
        for item in all_items(client):
            items.append(item)
            if len(items) == 7:
                break
        print("\npaginação preguiçosa: pegou 7 itens e parou:", items[:3], "...", "(só buscou 2 páginas de 4)")
        print("total:", len(list(all_items(client))), "itens em 4 páginas")
