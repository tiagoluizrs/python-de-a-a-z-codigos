"""Quatro gerações de formatação e a mini-linguagem de formatação."""
import datetime as dt
import decimal

name, price, qty = "Notebook", 3499.9, 3

# 1) operador %
print("%s custa %.2f (%d un.)" % (name, price, qty))
print("%(n)s x%(q)03d" % {"n": name, "q": qty})
# 2) str.format
print("{} custa {:.2f} ({} un.)".format(name, price, qty))
print("{1} {0} {1}".format("a", "b"), "{n}".format(n=name))
print("{0.real} {d[k]}".format(5, d={"k": "v"}))
# 3) f-string
print(f"{name} custa {price:.2f} ({qty} un.)")

# mini-linguagem: [[fill]align][sign][z][#][0][width][grouping][.prec][type]
n = 1234567.891
print(f"{n:,.2f}|{n:_.1f}|{n:>15,.0f}|{n:<15.1f}|{n:^15.0f}|")
print(f"{n:e}|{n:.3e}|{n:g}|{n:10.3g}|{0.5:%}|{0.12345:.1%}")
print(f"{42:5d}|{42:<5d}|{42:05d}|{42:+d}|{-42: d}|{42: d}")
print(f"{255:b}|{255:#b}|{255:08b}|{255:o}|{255:x}|{255:#X}|{255:#010x}")
print(f"{'ab':*^9}|{'ab':->6}|{'ab':.1}|{'abcdef':8.3}|")
print(f"{-0.0001:.2f}|{-0.0001:z.2f}")                   # 3.11+
print(f"{3.14159:{10}.{3}f}|{'x':{'>'}{5}}")              # aninhado
width, prec = 12, 2
print(f"[{n:{width},.{prec}f}]")

# conversões
text = "olá\n"
print(f"{text!s}|{text!r}|{text!a}|{'ç'!a}")

# = para depuração
x, items = 7, [1, 2, 3]
print(f"{x=} {x * 2=} {items=} {name=!r} {price=:.1f}")
print(f"{x = }")

# datas usam __format__ do objeto
moment = dt.datetime(2026, 10, 12, 9, 5)
print(f"{moment:%d/%m/%Y %H:%M}|{moment:%A}")
print(f"{decimal.Decimal('19.90'):>10.3f}|{True:d}|{None!s}")


class Temp:
    def __init__(self, c):
        self.c = c

    def __format__(self, spec):
        if spec == "f":
            return f"{self.c * 9 / 5 + 32:.1f}F"
        return f"{self.c:{spec or '.1f'}}C"


print(f"{Temp(21.5)}|{Temp(21.5):f}|{Temp(21.5):.3f}")
print(format(1234.5, ",.2f"), format("x", ">4"), (3).__format__("03"))

# o que mudou no 3.12 (PEP 701): mesmas aspas, várias linhas, barra invertida
songs = ["Alkaline", "Eden"]
print(f"{", ".join(songs)}")
print(f"{"\n".join(songs)}")
print(f"{
    len(songs)  # comentários e quebras dentro da expressão
}")
print(f"{{literal}} {{{x}}}")
