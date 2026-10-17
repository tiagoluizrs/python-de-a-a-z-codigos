"""Gabarito do exercício 4."""
import contextvars
import threading
from contextlib import contextmanager

_request_id = contextvars.ContextVar("request_id")
_user = contextvars.ContextVar("user")


@contextmanager
def request_scope(request_id, user=None):
    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("request_id inválido")
    id_token = _request_id.set(request_id)
    user_token = _user.set(user)
    try:
        yield
    finally:
        _user.reset(user_token)
        _request_id.reset(id_token)


def current_request_id():
    try:
        return _request_id.get()
    except LookupError:
        raise LookupError("fora de uma requisição") from None


def current_user():
    try:
        return _user.get()
    except LookupError:
        raise LookupError("fora de uma requisição") from None


def in_request():
    return _request_id.get(None) is not None


def log_prefix():
    if not in_request():
        return "[-] "
    return f"[{current_request_id()} {current_user() or 'anônimo'}] "


def run_in_thread(fn, *args):
    outcome = {}
    ctx = contextvars.copy_context()

    def target():
        try:
            outcome["value"] = ctx.run(fn, *args)
        except BaseException as error:
            outcome["error"] = error

    thread = threading.Thread(target=target)
    thread.start()
    thread.join()
    if "error" in outcome:
        raise outcome["error"]
    return outcome["value"]
