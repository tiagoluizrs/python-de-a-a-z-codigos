"""Um singleton vale por PROCESSO: cada processo filho cria o seu."""
import os
from concurrent.futures import ProcessPoolExecutor


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.owner_pid = os.getpid()
        return cls._instance


def who_owns(_=None):
    return Config().owner_pid, os.getpid()


def main():
    parent = Config().owner_pid
    with ProcessPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(who_owns, range(2)))
    print("pai:", parent == os.getpid())
    for owner, pid in results:
        print(f"filho {pid != parent}: o dono da instância é o próprio filho? {owner == pid} | é a instância do pai? {owner == parent}")
    print("cada processo tem a sua instância: para compartilhar de verdade entre processos, use um banco, um arquivo ou um servidor, nunca um objeto em memória")


if __name__ == "__main__":
    main()
