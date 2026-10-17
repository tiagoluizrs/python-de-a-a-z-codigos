"""Registrar exceções, contexto extra e o erro de logar e relançar."""
import io
import logging

buf = io.StringIO()
handler = logging.StreamHandler(buf)
handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
log = logging.getLogger("exc.demo")
log.addHandler(handler)
log.propagate = False
log.setLevel(logging.DEBUG)


def divide(a, b):
    return a / b


try:
    divide(1, 0)
except ZeroDivisionError:
    log.exception("falha ao dividir")                    # ERROR + traceback
out = buf.getvalue()
print(out.splitlines()[0], "|", out.splitlines()[-1], "| linhas:", len(out.splitlines()))

# exc_info em outros níveis; stack_info mostra de ONDE foi chamado
buf.truncate(0)
buf.seek(0)
try:
    divide(1, 0)
except ZeroDivisionError as error:
    log.warning("recuperado: %s", error, exc_info=True)
log.info("quem chamou?", stack_info=True)
print("traceback no warning:", "Traceback" in buf.getvalue(), "| Stack no info:", "Stack (most recent call last)" in buf.getvalue())

# extra: campos novos no registro (não podem colidir com os do LogRecord)
buf.truncate(0)
buf.seek(0)
handler.setFormatter(logging.Formatter("%(message)s user=%(user)s"))
log.info("login", extra={"user": "ana"})
print(buf.getvalue().strip())
try:
    log.info("x", extra={"message": "colide"})
except KeyError as error:
    print("KeyError:", error)

# LoggerAdapter: contexto fixo em todas as mensagens de um objeto
class Prefix(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f"[{self.extra['order']}] {msg}", kwargs


buf.truncate(0)
buf.seek(0)
handler.setFormatter(logging.Formatter("%(message)s"))
adapter = Prefix(log, {"order": "PED-42"})
adapter.info("pagamento aprovado")
print(buf.getvalue().strip())


# O anti-padrão: logar e relançar em todo nível (a mesma falha vira N linhas)
def low():
    try:
        divide(1, 0)
    except ZeroDivisionError:
        log.exception("low falhou")
        raise


def mid():
    try:
        low()
    except ZeroDivisionError:
        log.exception("mid falhou")
        raise


buf.truncate(0)
buf.seek(0)
try:
    mid()
except ZeroDivisionError:
    log.exception("topo falhou")
print("traceback repetido", buf.getvalue().count("Traceback"), "vezes para UMA falha")
