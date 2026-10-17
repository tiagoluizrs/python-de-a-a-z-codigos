"""Um servidor HTTP local para as demonstrações (nenhuma rede externa; HTTP/1.1 com keep-alive)."""
import contextlib
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


def make_handler(state):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):          # silêncio
            pass

        def _send(self, status, payload=None, headers=None, raw=None):
            body = raw if raw is not None else json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json" if raw is None else "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

        def _hit(self, key):
            with state["lock"]:
                state["hits"][key] = state["hits"].get(key, 0) + 1
                return state["hits"][key]

        def do_GET(self):
            url = urlparse(self.path)
            query = {k: v[0] for k, v in parse_qs(url.query).items()}
            path = url.path
            if path == "/json":
                self._send(200, {"ok": True, "items": [1, 2, 3]})
            elif path == "/echo":
                self._send(200, {"headers": {k.lower(): v for k, v in self.headers.items()}, "query": query, "path": self.path})
            elif path == "/slow":
                time.sleep(float(query.get("d", "0.2")))
                self._send(200, {"slept": float(query.get("d", "0.2"))})
            elif path.startswith("/status/"):
                self._send(int(path.rsplit("/", 1)[1]), {"status": int(path.rsplit("/", 1)[1])})
            elif path == "/flaky":                                   # falha as primeiras ?fail= vezes por ?key=
                count = self._hit("flaky:" + query.get("key", "k"))
                if count <= int(query.get("fail", "2")):
                    self._send(503, {"error": "indisponível", "attempt": count})
                else:
                    self._send(200, {"ok": True, "attempt": count})
            elif path == "/ratelimit":                               # 429 com Retry-After na primeira vez
                count = self._hit("rl:" + query.get("key", "k"))
                if count == 1:
                    self._send(429, {"error": "devagar"}, {"Retry-After": query.get("after", "1")})
                else:
                    self._send(200, {"ok": True})
            elif path.startswith("/redirect/"):
                n = int(path.rsplit("/", 1)[1])
                self._send(302, {"redirect": n}, {"Location": "/json" if n <= 1 else f"/redirect/{n - 1}"})
            elif path == "/pages":
                page = int(query.get("page", "1"))
                items = [f"item-{(page - 1) * 5 + i}" for i in range(1, 6)]
                self._send(200, {"items": items, "next": page + 1 if page < 4 else None})
            elif path == "/big":                                     # envia em pedaços: o servidor não aloca o corpo inteiro
                total = int(query.get("kb", "1024")) * 1024
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(total))
                self.end_headers()
                piece = b"x" * 65_536
                sent = 0
                while sent < total:
                    part = piece[: total - sent]
                    self.wfile.write(part)
                    sent += len(part)
            elif path == "/range":
                data = bytes(range(256)) * 400
                header = self.headers.get("Range")
                if header and header.startswith("bytes="):
                    start = int(header[6:].split("-")[0])
                    chunk = data[start:]
                    self._send(206, raw=chunk, headers={"Content-Range": f"bytes {start}-{len(data) - 1}/{len(data)}"})
                else:
                    self._send(200, raw=data)
            elif path == "/stream":
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                for i in range(int(query.get("n", "5"))):
                    line = f"linha {i}\n".encode()
                    self.wfile.write(f"{len(line):x}\r\n".encode() + line + b"\r\n")
                    self.wfile.flush()
                    time.sleep(0.05)
                self.wfile.write(b"0\r\n\r\n")
            elif path == "/secure":
                token = self.headers.get("Authorization", "")
                if token == "Bearer valid":
                    self._send(200, {"user": "ana"})
                else:
                    self._send(401, {"error": "token inválido"}, {"WWW-Authenticate": "Bearer"})
            elif path == "/cookie":
                self._send(200, {"ok": True}, {"Set-Cookie": "session=abc123; Path=/; HttpOnly"})
            elif path == "/hits":
                self._send(200, state["hits"])
            else:
                self._send(404, {"error": "não encontrado", "path": path})

        def do_POST(self):
            if self.headers.get("Transfer-Encoding", "").lower() == "chunked":      # corpo enviado em pedaços (upload por gerador)
                body = b""
                while True:
                    size = int(self.rfile.readline().strip() or b"0", 16)
                    if size == 0:
                        self.rfile.readline()
                        break
                    body += self.rfile.read(size)
                    self.rfile.readline()
            else:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length) if length else b""
            if self.path == "/items":
                try:
                    data = json.loads(body or b"{}")
                except json.JSONDecodeError:
                    self._send(400, {"error": "JSON inválido"})
                    return
                self._send(201, {"created": data, "id": 42})
            elif self.path == "/upload":
                self._send(200, {"received_bytes": len(body), "content_type": self.headers.get("Content-Type", "")})
            else:
                self._send(404, {"error": "não encontrado"})

    return Handler


@contextlib.contextmanager
def serve():
    state = {"hits": {}, "lock": threading.Lock()}
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(state))
    server.daemon_threads = True
    server.handle_error = lambda request, client_address: None      # cliente que desiste (timeout) não deve poluir a saída
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    with serve() as url:
        print("servidor de demonstração em", url, "(Ctrl+C para sair)")
        threading.Event().wait()
