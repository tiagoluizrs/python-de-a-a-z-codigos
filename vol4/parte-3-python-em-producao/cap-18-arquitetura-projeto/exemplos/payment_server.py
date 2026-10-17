"""Um 'serviço de pagamentos' local para os exemplos (stdlib): aprova até 10.000 e recusa acima."""
import json
import threading
import time
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LATENCY = 0.005                                                   # 5 ms: uma chamada de rede razoável


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        time.sleep(LATENCY)
        approved = Decimal(data["amount"]) <= Decimal("10000")
        body = json.dumps({"approved": approved, "reference": f"pay-{data['order_id']}", "reason": "" if approved else "limite excedido"}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"
