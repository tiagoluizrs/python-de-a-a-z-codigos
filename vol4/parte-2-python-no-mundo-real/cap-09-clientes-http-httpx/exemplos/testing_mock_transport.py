"""Testar código HTTP sem rede: MockTransport e respx."""
import httpx
import respx

calls = []


def handler(request: httpx.Request) -> httpx.Response:
    calls.append((request.method, request.url.path, request.headers.get("authorization")))
    if request.url.path == "/users/1":
        return httpx.Response(200, json={"id": 1, "name": "Ana"})
    if request.url.path == "/users":
        return httpx.Response(201, json={"id": 2, **__import__("json").loads(request.content)})
    if request.url.path == "/broken":
        return httpx.Response(503, text="fora do ar")
    return httpx.Response(404)


# 1. a lógica de negócio recebe um Client; o teste injeta o transporte falso
def get_user(client: httpx.Client, user_id: int) -> dict:
    response = client.get(f"/users/{user_id}")
    response.raise_for_status()
    return response.json()


with httpx.Client(transport=httpx.MockTransport(handler), base_url="http://api.test", headers={"Authorization": "Bearer t"}) as client:
    print("MockTransport:", get_user(client, 1), "| chamadas:", calls)
    try:
        get_user(client, 99)
    except httpx.HTTPStatusError as error:
        print("404 simulado levantou HTTPStatusError:", error.response.status_code)
    print("503 simulado:", client.get("/broken").status_code, "| POST:", client.post("/users", json={"name": "Bia"}).json())


# 2. simular falhas de REDE: o handler levanta a exceção
def flaky(request):
    raise httpx.ConnectTimeout("simulado", request=request)


with httpx.Client(transport=httpx.MockTransport(flaky)) as client:
    try:
        client.get("http://api.test/x")
    except httpx.ConnectTimeout:
        print("\nfalha de conexão simulada: ConnectTimeout (impossível de provocar de forma confiável contra um servidor real)")

# 3. respx: rotas declarativas, e verificação de chamadas
with respx.mock(base_url="http://api.test") as router:
    route = router.get("/users/7").respond(200, json={"id": 7, "name": "Caio"})
    router.get("/slow").mock(side_effect=httpx.ReadTimeout("simulado"))
    print("\nrespx:", httpx.get("http://api.test/users/7").json(), "| chamou?", route.called, "| vezes:", route.call_count)
    try:
        httpx.get("http://api.test/slow")
    except httpx.ReadTimeout:
        print("respx simulou ReadTimeout")

print("\nregra: o código recebe o cliente (injeção de dependência); o teste troca o TRANSPORTE, não o código. Teste também contra um servidor real (demo_server).")
