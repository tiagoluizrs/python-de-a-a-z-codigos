"""O que um formatador faz (e o que ele não decide): estilo, vírgula final, aspas."""
import subprocess
import sys

SOURCE = """
def f(a,b = 1,*args,**kw):
    x = {'a':1,'b':[1,2,3],  "c" : (4,5)}
    y = [ 1,2,3 ]
    z = call_something(argument_number_one, argument_number_two, argument_number_three, argument_four)
    w = call(a, b,)
    return x,y,z,w
"""


def fmt(source, *extra):
    result = subprocess.run([sys.executable, "-m", "ruff", "format", "--isolated", *extra, "--stdin-filename", "x.py", "-"],
                            input=source, capture_output=True, text=True, encoding="utf-8")
    return result.stdout


once = fmt(SOURCE)
print(once)
print("idempotente (formatar de novo não muda nada):", fmt(once) == once)
print("aspas simples para preferência:", "'a'" in fmt(SOURCE, "--config", "format.quote-style='single'"))
