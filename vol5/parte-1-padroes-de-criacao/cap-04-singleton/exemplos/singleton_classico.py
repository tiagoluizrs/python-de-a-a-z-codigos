"""Singleton, forma clássica: garantir UMA instância e um ponto de acesso global. E as quatro armadilhas que ela traz."""
import threading
import time


# --- 1. a versão ingênua: __new__ guarda a instância ---
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.values = {}                                   # armadilha 1: __init__ roda a CADA chamada de Config()


a = Config()
a.values["debug"] = True
b = Config()                                               # mesma instância... mas __init__ rodou de novo
print("mesma instância:", a is b, "| mas o estado foi apagado pelo __init__:", b.values)


# --- 2. consertando: criar o estado uma única vez ---
class Config2:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.values = {}                      # o estado nasce com a instância, não no __init__
        return cls._instance


a = Config2()
a.values["debug"] = True
print("\nestado na criação:", Config2().values, "| mesma instância:", a is Config2())


# --- 3. armadilha 2: threads. Sem trava, duas threads podem criar duas instâncias ---
class Slow:
    _instance = None
    created = 0

    def __new__(cls):
        if cls._instance is None:
            time.sleep(0.01)                               # simula uma criação cara (ler um arquivo, abrir uma conexão)
            cls._instance = super().__new__(cls)
            cls.created += 1
        return cls._instance


def hammer(factory, threads=8):
    barrier = threading.Barrier(threads)
    found = []

    def work():
        barrier.wait()
        found.append(factory())

    workers = [threading.Thread(target=work) for _ in range(threads)]
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    return found


found = hammer(Slow)
print(f"\nsem trava: {Slow.created} instâncias criadas por 8 threads | objetos distintos devolvidos: {len({id(x) for x in found})}")


class Locked:
    _instance = None
    _lock = threading.Lock()
    created = 0

    def __new__(cls):
        if cls._instance is None:                          # verificação rápida, sem trava (o caso comum)
            with cls._lock:
                if cls._instance is None:                  # verificação de novo, já com a trava (double-checked locking)
                    time.sleep(0.01)
                    cls._instance = super().__new__(cls)
                    cls.created += 1
        return cls._instance


found = hammer(Locked)
print(f"com trava e dupla verificação: {Locked.created} instância criada | objetos distintos: {len({id(x) for x in found})}")


# --- 4. outras formas clássicas: decorador e metaclasse ---
def singleton(cls):
    instances = {}
    lock = threading.Lock()

    def get(*args, **kwargs):
        with lock:
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    get.__wrapped__ = cls
    return get


@singleton
class Pool:
    def __init__(self, size=4):
        self.size = size


print("\ndecorador:", Pool(8).size, Pool(2).size, "(os argumentos da 2ª chamada são ignorados em silêncio)")
print("o decorador troca a CLASSE por uma função: isinstance(Pool(), Pool) ->", end=" ")
try:
    print(isinstance(Pool(), Pool))
except TypeError as error:
    print("TypeError:", error)


class SingletonMeta(type):
    _instances: dict = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(metaclass=SingletonMeta):
    def __init__(self):
        self.lines = []


print("metaclasse:", Logger() is Logger(), "| a classe continua sendo uma classe:", isinstance(Logger(), Logger))


# --- 5. armadilha 3: o estado global sobrevive entre os testes ---
class Counter:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.n = 0
        return cls._instance


def test_a():
    Counter().n += 1
    return Counter().n


def test_b():
    return Counter().n


print("\ntestes em sequência compartilham o estado: test_a ->", test_a(), "| test_b (esperava 0) ->", test_b())
print("o singleton é uma variável global com nome de padrão: qualquer teste enxerga o que o anterior deixou")

# --- 6. armadilha 4: processos. Cada processo tem a SUA instância ---
print("\nem multiprocessing (spawn ou fork) cada processo cria a sua: o 'singleton' vale por processo, não por programa")
