"""Gabarito do exercício 4."""
import asyncio
import contextvars
import logging
import threading

_request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


def get_request_id():
    return _request_id.get()


class request_context:
    def __init__(self, request_id):
        self.request_id = request_id
        self._token = None

    def __enter__(self):
        self._token = _request_id.set(self.request_id)
        return self

    def __exit__(self, *exc):
        _request_id.reset(self._token)
        return False


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True


async def fan_out(request_id, count):
    async def one():
        await asyncio.sleep(0)
        return get_request_id()

    with request_context(request_id):
        tasks = [asyncio.create_task(one()) for _ in range(count)]
        return list(await asyncio.gather(*tasks))


def run_in_thread(fn, *args):
    ctx = contextvars.copy_context()
    box = {}

    def target():
        box["value"] = ctx.run(fn, *args)

    thread = threading.Thread(target=target)
    thread.start()
    thread.join()
    return box["value"]
