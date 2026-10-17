"""Gabarito do exercício 2."""


def first_match(handlers, request, default=None):
    for handler in handlers:
        result = handler(request)
        if result is not None:
            return result
    return default


class Router:
    def __init__(self, fallback=None):
        self._routes = []
        self._fallback = fallback

    def register(self, predicate, handler):
        self._routes.append((predicate, handler))
        return handler

    def insert(self, index, predicate, handler):
        self._routes.insert(index, (predicate, handler))

    def remove(self, handler):
        before = len(self._routes)
        self._routes = [(p, h) for p, h in self._routes if h is not handler]
        return before - len(self._routes)

    def route(self, request):
        for predicate, handler in self._routes:
            if predicate(request):
                return handler(request)
        if self._fallback is not None:
            return self._fallback(request)
        raise LookupError(f"nenhuma rota para {request!r}")

    def handlers(self):
        return [h for _, h in self._routes]

    def __len__(self):
        return len(self._routes)


def _empty(text):
    if not text.strip():
        return "vazia"


def _spam(text):
    if "compre agora" in text.lower():
        return "spam"


def _urgent(text):
    if "urgente" in text.lower() or text.endswith("!!!"):
        return "urgente"


def _question(text):
    if text.endswith("?"):
        return "pergunta"


def classify(text):
    return first_match([_empty, _spam, _urgent, _question], text, default="comum")
