"""O traceback por dentro: frames, extract_tb e clear_frames."""
import traceback


def a():
    b()


def b():
    c()


def c():
    big = bytearray(10_000_000)
    raise ValueError("fundo")


try:
    a()
except ValueError as error:
    tb = error.__traceback__
    while tb:
        print(tb.tb_frame.f_code.co_name, "linha", tb.tb_lineno)
        tb = tb.tb_next
    summary = traceback.extract_tb(error.__traceback__)
    print([(f.name, f.lineno) for f in summary])

    # O traceback mantém os frames (e as variáveis locais) vivos
    innermost = list(traceback.walk_tb(error.__traceback__))[-1][0]
    print("locais vivos:", sorted(innermost.f_locals))
    traceback.clear_frames(error.__traceback__)
    print("depois de clear_frames:", sorted(innermost.f_locals))


# Sugestões do Python aparecem na exibição do traceback, não em str(error)
class Box:
    def lenght(self):
        pass


try:
    Box().length
except AttributeError as error:
    print("str(error):", error)
    print(traceback.format_exception(error)[-1].strip())
