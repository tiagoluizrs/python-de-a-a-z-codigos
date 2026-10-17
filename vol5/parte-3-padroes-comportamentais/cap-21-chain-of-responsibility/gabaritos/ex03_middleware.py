"""Gabarito do exercício 3."""
from collections import defaultdict, deque


def compose(*middlewares):
    def wrap(handler):
        for mw in reversed(middlewares):
            if not callable(mw):
                raise TypeError("middleware precisa ser chamável")
            handler = (lambda mw_, nxt: lambda request: mw_(request, nxt))(mw, handler)
        return handler

    return wrap


def logging_mw(log):
    def middleware(request, call_next):
        log.append(f"-> {request['path']}")
        try:
            response = call_next(request)
        except Exception as error:
            log.append(f"!! {type(error).__name__}")
            raise
        log.append(f"<- {response['status']}")
        return response

    return middleware


def auth_mw(valid_tokens):
    def middleware(request, call_next):
        if request.get("token") not in valid_tokens:
            return {"status": 401, "body": "não autorizado"}
        return call_next(request)

    return middleware


def rate_limit_mw(limit, window, clock):
    if limit < 1 or window <= 0:
        raise ValueError("limit e window inválidos")
    seen = defaultdict(deque)

    def middleware(request, call_next):
        client = request.get("client", "anon")
        now = clock()
        times = seen[client]
        while times and now - times[0] >= window:
            times.popleft()
        if len(times) >= limit:
            return {"status": 429, "body": "muitos pedidos"}
        times.append(now)
        return call_next(request)

    return middleware


def cache_mw(methods=("GET",)):
    store = {}

    def middleware(request, call_next):
        method, path = request.get("method", "GET"), request["path"]
        if method not in methods:
            store.pop(path, None)
            return call_next(request)
        if path in store:
            return {**store[path], "cached": True}
        response = call_next(request)
        if response.get("status") == 200:
            store[path] = dict(response)
        return response

    return middleware
