"""Custo de montar texto: += em laço, join, io.StringIO e formatação."""
import io
import sys
import timeit


def plus_equals(n):
    out = ""
    for i in range(n):
        out += "line " + str(i) + "\n"
    return out


def join_list(n):
    return "".join(["line " + str(i) + "\n" for i in range(n)])


def join_generator(n):
    return "".join("line " + str(i) + "\n" for i in range(n))


def string_io(n):
    buffer = io.StringIO()
    for i in range(n):
        buffer.write(f"line {i}\n")
    return buffer.getvalue()


assert plus_equals(10) == join_list(10) == string_io(10)

print(f"{'n':>9} {'+= (ms)':>10} {'join list':>10} "
      f"{'join gen':>10} {'StringIO':>10}")
for n in (1_000, 10_000, 100_000, 1_000_000):
    row = []
    for fn in (plus_equals, join_list, join_generator, string_io):
        runs = 3 if n < 1_000_000 else 1
        best = min(timeit.repeat(lambda: fn(n), number=1, repeat=runs))
        row.append(best * 1000)
    print(f"{n:>9} " + " ".join(f"{v:>10.1f}" for v in row))
