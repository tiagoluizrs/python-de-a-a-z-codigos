"""__del__, weakref.finalize e o que `del` realmente faz."""
import gc
import weakref


class Resource:
    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        print(f"  __del__ de {self.name}")


print("1) del remove o nome; __del__ roda ao zerar o contador")
r = Resource("r1")
alias = r
del r
print("  nome removido, objeto vivo:", alias.name)
del alias

print("2) o traceback segura o frame (e o local) até o fim do except")


def work() -> None:
    res = Resource("r2")
    raise RuntimeError("falha")


try:
    work()
except RuntimeError:
    print("  dentro do except: res ainda vive no traceback")

print("  fora do except: o __del__ acima já rodou")

print("3) ciclo com __del__ (PEP 442): o gc consegue finalizar")
a = Resource("ciclo-a")
b = Resource("ciclo-b")
a.other, b.other = b, a
del a, b
print("  nenhum __del__ ainda (contador não zerou)")
print("  coletados:", gc.collect() > 0)
print("  gc.garbage:", gc.garbage)

print("4) weakref.finalize: alternativa robusta ao __del__")


def release(name: str) -> None:
    print(f"  liberando {name}")


obj = Resource("r4")
fin = weakref.finalize(obj, release, obj.name)
print("  vivo:", fin.alive)
del obj
print("  vivo:", fin.alive)

print("  finalize com atexit=True roda no encerramento:")
keeper = Resource("r5")
weakref.finalize(keeper, release, keeper.name)
print("fim do script")
