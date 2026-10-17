"""basicConfig, estilos de formato e o que cada campo do formato traz."""
import io
import logging

buf = io.StringIO()
logging.basicConfig(
    stream=buf,
    level=logging.DEBUG,
    format="{asctime} | {levelname:<8} | {name} | {funcName}:{lineno} | {message}",
    style="{",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("demo")


def work():
    log.debug("começou %s", "agora")
    log.info("meio")
    log.warning("atenção")


work()
print(buf.getvalue(), end="")

# basicConfig é no-op se a raiz já tem handlers, a menos que force=True
buf2 = io.StringIO()
logging.basicConfig(stream=buf2, format="%(message)s")
log.info("vai para onde?")
print("buf2 vazio:", buf2.getvalue() == "", "| buf recebeu:", "vai para onde?" in buf.getvalue())
logging.basicConfig(stream=buf2, format="%(message)s", force=True)
log.info("agora sim")
print("buf2:", buf2.getvalue().strip())

# defaults= (3.10): valores padrão para campos de extra
buf3 = io.StringIO()
handler = logging.StreamHandler(buf3)
handler.setFormatter(logging.Formatter("%(message)s [req=%(request_id)s]", defaults={"request_id": "-"}))
other = logging.getLogger("demo.other")
other.propagate = False
other.addHandler(handler)
other.warning("sem extra")
other.warning("com extra", extra={"request_id": "abc123"})
print(buf3.getvalue().strip())
