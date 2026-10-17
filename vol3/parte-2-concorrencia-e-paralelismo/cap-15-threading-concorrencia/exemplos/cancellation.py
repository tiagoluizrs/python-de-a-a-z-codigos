"""Parar threads: cooperação, não força. Não existe Thread.kill()."""
import threading
import time

print("a thread tem método para ser morta?", hasattr(threading.Thread, "kill") or hasattr(threading.Thread, "terminate"))

# O jeito certo: a thread VERIFICA um sinal
stop = threading.Event()
ticks = []


def loop():
    while not stop.is_set():
        ticks.append(time.perf_counter())
        stop.wait(0.01)                       # espera interrompível (melhor que sleep)


t = threading.Thread(target=loop)
t.start()
time.sleep(0.1)
start = time.perf_counter()
stop.set()
t.join()
print(f"parou em {(time.perf_counter() - start) * 1e3:.1f} ms depois do set(); {len(ticks)} iterações")

# sleep() não é interrompível: a parada espera o sleep inteiro
stop2 = threading.Event()


def sleepy():
    while not stop2.is_set():
        time.sleep(0.3)


t = threading.Thread(target=sleepy)
t.start()
time.sleep(0.05)
start = time.perf_counter()
stop2.set()
t.join()
print(f"com time.sleep(0.3), a parada levou {(time.perf_counter() - start) * 1e3:.0f} ms (até o sleep acabar)")

# Timer: executar depois de um tempo, cancelável
fired = []
timer = threading.Timer(0.1, lambda: fired.append("disparou"))
timer.start()
timer.cancel()
time.sleep(0.15)
print("Timer cancelado antes de disparar:", fired == [])

# Daemon: morre junto com o programa, SEM limpeza
print("thread daemon: nasce com daemon=True; o interpretador não a espera ao terminar (finalizadores não rodam)")
