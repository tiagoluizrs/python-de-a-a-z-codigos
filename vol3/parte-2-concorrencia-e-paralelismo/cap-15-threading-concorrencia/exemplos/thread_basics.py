"""Criar, iniciar, esperar; devolver resultados e tratar exceções em threads."""
import queue
import threading
import time


def worker(name, delay, results):
    time.sleep(delay)
    results.append((name, threading.current_thread().name))


results = []
threads = [threading.Thread(target=worker, args=(f"t{i}", 0.05 * (3 - i), results), name=f"trabalhador-{i}") for i in range(3)]
for t in threads:
    t.start()
print("vivas logo após start():", [t.is_alive() for t in threads], "| ativas:", threading.active_count())
for t in threads:
    t.join()
print("terminaram na ordem do TEMPO, não da criação:", results)


# Devolver um valor: thread não tem "retorno": use uma fila, uma lista ou uma subclasse
class ResultThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()
        self._func, self._args = func, args
        self.value = self.error = None

    def run(self):
        try:
            self.value = self._func(*self._args)
        except BaseException as exc:              # noqa: BLE001
            self.error = exc

    def result(self, timeout=None):
        self.join(timeout)
        if self.is_alive():
            raise TimeoutError("a thread ainda não terminou")
        if self.error:
            raise self.error
        return self.value


t = ResultThread(pow, 2, 100)
t.start()
print("resultado:", t.result(), "| com erro:", end=" ")
t = ResultThread(lambda: 1 / 0)
t.start()
try:
    t.result()
except ZeroDivisionError as error:
    print("ZeroDivisionError propagou para quem chamou result():", error)

# Uma exceção NÃO tratada em uma thread não derruba o programa: vai para threading.excepthook
caught = []
threading.excepthook = lambda args: caught.append((args.thread.name, args.exc_type.__name__, str(args.exc_value)))
boom = threading.Thread(target=lambda: 1 / 0, name="falhosa")
boom.start()
boom.join()
print("excepthook recebeu:", caught, "| o programa continua")
threading.excepthook = threading.__excepthook__

# join com timeout não mata a thread: só desiste de esperar
stop = threading.Event()
slow = threading.Thread(target=stop.wait)
slow.start()
slow.join(timeout=0.05)
print("depois de join(0.05) a thread ainda vive:", slow.is_alive())
stop.set()
slow.join()
print("depois do set():", slow.is_alive())

# daemon: não impede o programa de terminar
print("daemon da thread principal:", threading.main_thread().daemon, "| nome:", threading.current_thread().name)
