"""Gabarito do exercício 6."""
import re

SENSITIVE_HEADERS = {"authorization", "proxy-authorization", "cookie", "set-cookie", "x-api-key"}
SENSITIVE_PARAMS = {"token", "api_key", "apikey", "password", "secret", "access_token"}


def redact_url(url):
    url = re.sub(r"(?<=://)[^/@\s]+@", "***@", str(url))
    query_start = url.find("?")
    if query_start == -1:
        return url
    base, query = url[:query_start], url[query_start + 1:]
    parts = []
    for part in query.split("&"):
        name, sep, value = part.partition("=")
        parts.append(f"{name}=***" if sep and name.lower() in SENSITIVE_PARAMS else part)
    return base + "?" + "&".join(parts)


def redact_headers(headers):
    return {k.lower(): ("***" if k.lower() in SENSITIVE_HEADERS else v) for k, v in dict(headers).items()}


class RequestLog:
    def __init__(self):
        self.records = []

    def hook(self, response):
        request = response.request
        try:
            ms = response.elapsed.total_seconds() * 1e3
        except RuntimeError:
            ms = 0.0
        self.records.append({"method": request.method, "url": redact_url(request.url), "status": response.status_code,
                             "headers": redact_headers(request.headers), "ms": ms})

    def errors(self):
        return [r for r in self.records if r["status"] >= 400]
