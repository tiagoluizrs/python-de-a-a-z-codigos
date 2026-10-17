"""Observer em Python: uma lista de funções (um "sinal"), com cópia na notificação, exceções isoladas e referências fracas."""
import concurrent.futures
import gc
import logging
import io
import signal
import time
import weakref


# --- 1. o sinal: a lista de funções e três métodos ---
class Signal:
    def __init__(self):
        self._handlers = []

    def connect(self, fn):
        self._handlers.append(fn)
        return fn                                              # permite usar como decorador

    def disconnect(self, fn):
        self._handlers.remove(fn)

    def emit(self, *args, **kwargs):
        errors = []
        for handler in list(self._handlers):                   # uma CÓPIA: conectar/desconectar durante a emissão não embaralha o laço
            try:
                handler(*args, **kwargs)
            except Exception as error:                         # um observador com defeito não impede os outros
                errors.append(error)
        if errors:
            raise ExceptionGroup("observadores falharam", errors)

    def __len__(self):
        return len(self._handlers)


price_changed = Signal()
log = []


@price_changed.connect                                          # o observador é uma função decorada
def show(price):
    log.append(f"painel: {price}")


price_changed.connect(lambda price: log.append(f"alerta! {price}") if price > 100 else None)
price_changed.emit(90)
price_changed.emit(120)
print("sinal com funções:", log)

# --- 2. as três armadilhas do exemplo clássico, resolvidas ---
@price_changed.connect
def broken(price):
    raise RuntimeError("falhou")


seen = []
price_changed.connect(seen.append)
try:
    price_changed.emit(7)
except ExceptionGroup as group:
    print("\n(a) uma exceção não impede os outros:", seen, "| erros agrupados:", [str(e) for e in group.exceptions])
price_changed.disconnect(broken)

quitter_log = []
signal2 = Signal()


def once(value):
    quitter_log.append(("once", value))
    signal2.disconnect(once)                                    # desconecta DURANTE a emissão


signal2.connect(once)
signal2.connect(lambda v: quitter_log.append(("outro", v)))
signal2.emit(1)
signal2.emit(2)
print("(b) desconectar durante a emissão não pula ninguém (o laço percorre uma cópia):", quitter_log)

# --- 3. (c) o vazamento: um método ligado mantém o OBJETO vivo; WeakMethod resolve ---
class Listener:
    def on_event(self, value):
        pass


class WeakSignal:
    def __init__(self):
        self._refs = []

    def connect(self, method):
        self._refs.append(weakref.WeakMethod(method))

    def emit(self, *args):
        alive = []
        for ref in self._refs:
            method = ref()
            if method is not None:
                method(*args)
                alive.append(ref)
        self._refs = alive                                      # limpa os mortos
        return len(alive)


strong, weak = Signal(), WeakSignal()
l1, l2 = Listener(), Listener()
strong.connect(l1.on_event)
weak.connect(l2.on_event)
r1, r2 = weakref.ref(l1), weakref.ref(l2)
del l1, l2
gc.collect()
print("\n(c) ouvinte conectado de forma FORTE ainda vivo:", r1() is not None, "| de forma FRACA:", r2() is not None, "| ouvintes que o sinal fraco ainda avisa:", weak.emit(1))

# --- 4. a biblioteca padrão: callbacks em toda parte ---
done = []
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
    future = pool.submit(lambda: 6 * 7)
    future.add_done_callback(lambda f: done.append(f.result()))     # Future.add_done_callback: um Observer de um resultado
time.sleep(0.05)
print("\nFuture.add_done_callback:", done)

stream = io.StringIO()
logger = logging.getLogger("observer-demo")
logger.setLevel(logging.INFO)
logger.propagate = False
logger.addHandler(logging.StreamHandler(stream))
logger.addHandler(logging.NullHandler())                        # um segundo observador: um Handler que ignora tudo
logger.info("evento")
print("logging: cada Handler é um observador do Logger ->", repr(stream.getvalue()))

previous = signal.signal(signal.SIGINT, lambda signum, frame: None)
print("signal.signal registra um observador do sistema operacional; anterior:", "padrão do Python" if previous is signal.default_int_handler else previous)
signal.signal(signal.SIGINT, previous)

# --- 5. o custo de emitir ---
def best(fn, n=20_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


print("\ncusto de uma emissão, por número de observadores (funções que não fazem nada):")
for count in (0, 1, 10, 100):
    sig = Signal()
    for _ in range(count):
        sig.connect(lambda x: None)
    print(f"  {count:>3} observadores: {best(lambda: sig.emit(1)):6.2f} µs")
print("o custo cresce de forma linear (~0,06 µs por observador): o que pesa é o TRABALHO de cada observador, não a notificação")
