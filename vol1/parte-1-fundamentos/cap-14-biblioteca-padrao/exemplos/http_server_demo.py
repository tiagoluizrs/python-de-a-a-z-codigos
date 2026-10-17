"""Servidor http.server em thread, servindo uma pasta temporária."""
import tempfile
import threading
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silencia o log de acessos no stderr



class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silencia o log de acessos no stderr


with tempfile.TemporaryDirectory() as tmp:
    Path(tmp, "hello.txt").write_text("olá, servidor!", encoding="utf-8")
    handler = partial(QuietHandler, directory=tmp)
    # porta 0: o sistema escolhe uma porta livre; só escuta em loopback
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{port}/hello.txt"
        with urllib.request.urlopen(url, timeout=5) as resp:
            print(resp.status, resp.headers["Content-Type"])
            print(resp.read().decode("utf-8"))
        server.shutdown()
        thread.join()
