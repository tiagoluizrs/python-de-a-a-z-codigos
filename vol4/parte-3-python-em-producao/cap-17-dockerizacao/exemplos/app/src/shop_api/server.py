"""Um serviço HTTP pequeno, com o comportamento que um contêiner precisa ter."""
import os
import signal
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import orjson
from pydantic import BaseModel

from shop_api import __version__

STARTED = time.time()
HELD: list[bytearray] = []                              # memória segurada de propósito (/alloc)


class Info(BaseModel):
    service: str = "shop-api"
    version: str = __version__
    python: str
    pid: int
    uid: int | None
    env: str
    uptime_s: float


def uid() -> int | None:
    return os.getuid() if hasattr(os, "getuid") else None


def redis_client():
    url = os.environ.get("REDIS_URL")
    if not url:
        return None
    import redis                                         # import tardio: só quem usa o Redis paga

    return redis.Redis.from_url(url, socket_timeout=2)


class Handler(BaseHTTPRequestHandler):
    server_version = "shop-api"

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}", flush=True)           # logs em stdout: o Docker coleta

    def reply(self, status: int, payload) -> None:
        body = orjson.dumps(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        if url.path == "/":
            info = Info(python=sys.version.split()[0], pid=os.getpid(), uid=uid(), env=os.environ.get("APP_ENV", "dev"),
                        uptime_s=round(time.time() - STARTED, 2))
            self.reply(200, info.model_dump())
        elif url.path == "/healthz":
            self.reply(200, {"status": "ok"})
        elif url.path == "/slow":
            time.sleep(float(query.get("s", 1)))
            self.reply(200, {"slept": float(query.get("s", 1))})
        elif url.path == "/alloc":
            mb = int(query.get("mb", 10))
            block = bytearray(mb * 1024 * 1024)
            for i in range(0, len(block), 4096):             # toca cada página: a memória é REALMENTE usada
                block[i] = 1
            HELD.append(block)
            self.reply(200, {"held_mb": sum(len(b) for b in HELD) // (1024 * 1024)})
        elif url.path == "/count":
            client = redis_client()
            if client is None:
                self.reply(503, {"error": "REDIS_URL não definido"})
            else:
                self.reply(200, {"count": client.incr("hits")})
        else:
            self.reply(404, {"error": "não encontrado"})


def main() -> int:
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)         # 0.0.0.0: dentro do contêiner, 127.0.0.1 não seria alcançável de fora
    server.daemon_threads = False
    stop = threading.Event()

    def on_sigterm(signum, frame):
        print("SIGTERM recebido: terminando as requisições em andamento", flush=True)
        stop.set()
        threading.Thread(target=server.shutdown).start()           # shutdown() de outra thread, ou trava o serve_forever

    signal.signal(signal.SIGTERM, on_sigterm)
    signal.signal(signal.SIGINT, on_sigterm)
    print(f"shop-api {__version__} ouvindo em :{port} como uid={uid()} pid={os.getpid()}", flush=True)
    server.serve_forever()
    server.server_close()                                          # espera as threads de requisição (daemon_threads = False)
    print("encerrado com limpeza", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
