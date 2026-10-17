"""Logs estruturados em JSON, com contexto de requisição via contextvars."""
import contextvars
import io
import json
import logging
from datetime import UTC, datetime

REQUEST_ID = contextvars.ContextVar("request_id", default="-")

STANDARD = set(vars(logging.LogRecord("", 0, "", 0, "", (), None))) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        data = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in vars(record).items():
            if key not in STANDARD:
                data[key] = value
        if record.exc_info:
            data["exc"] = self.formatException(record.exc_info)
        return json.dumps(data, ensure_ascii=False, default=str)


class ContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = REQUEST_ID.get()
        return True


buf = io.StringIO()
handler = logging.StreamHandler(buf)
handler.setFormatter(JsonFormatter())
handler.addFilter(ContextFilter())
log = logging.getLogger("structured")
log.addHandler(handler)
log.propagate = False
log.setLevel(logging.INFO)

REQUEST_ID.set("req-7")
log.info("pedido criado", extra={"order_id": 42, "total": 99.9})
try:
    1 / 0
except ZeroDivisionError:
    log.exception("falha")

for line in buf.getvalue().splitlines():
    record = json.loads(line)                                      # cada linha é um JSON completo
    record.pop("exc", None)
    print(record)

# Isolamento de contexto entre threads e tarefas
import asyncio
import threading

print("thread nova vê:", end=" ")
t = threading.Thread(target=lambda: print(REQUEST_ID.get()))
t.start()
t.join()


async def handle(rid):
    REQUEST_ID.set(rid)
    await asyncio.sleep(0.01)
    return REQUEST_ID.get()


async def main():
    return await asyncio.gather(handle("a"), handle("b"), handle("c"))


print("3 tarefas simultâneas:", asyncio.run(main()), "| contexto principal:", REQUEST_ID.get())
