"""Gabarito do exercício 4."""
import httpx


class ApiError(Exception):
    def __init__(self, status, message, body=None):
        super().__init__(f"{status}: {message}" if status else message)
        self.status, self.message, self.body = status, message, body


class TokenAuth(httpx.Auth):
    def __init__(self, token, refresh=None):
        self.token, self.refresh = token, refresh

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        response = yield request
        if response.status_code == 401 and self.refresh is not None:
            self.token = self.refresh()
            request.headers["Authorization"] = f"Bearer {self.token}"
            yield request


class ApiClient:
    def __init__(self, base_url, token, *, refresh=None, transport=None, timeout=5.0):
        self._client = httpx.Client(base_url=base_url, auth=TokenAuth(token, refresh), timeout=timeout, transport=transport)

    def _send(self, method, path, **kwargs):
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.RequestError as error:
            raise ApiError(None, f"falha de rede: {type(error).__name__}") from error
        if response.status_code >= 400:
            try:
                body = response.json()
            except ValueError:
                body = response.text
            message = None
            if isinstance(body, dict):
                message = body.get("error") or body.get("message")
            elif isinstance(body, str) and body:
                message = body
            raise ApiError(response.status_code, message or f"HTTP {response.status_code}", body)
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError as error:
            raise ApiError(response.status_code, "resposta não é JSON") from error

    def get(self, path, **params):
        return self._send("GET", path, params=params)

    def post(self, path, payload):
        return self._send("POST", path, json=payload)

    def delete(self, path):
        return self._send("DELETE", path)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False
