"""Como o deepcopy usa o memo: compartilhamento e ciclos preservados."""
import copy

# 1) Compartilhamento interno é preservado
shared = ["x"]
box = {"a": shared, "b": shared}
clone = copy.deepcopy(box)
print("a is b no clone:", clone["a"] is clone["b"])
print("clone['a'] is shared:", clone["a"] is shared)

# 2) Ciclos não causam recursão infinita
loop = [1]
loop.append(loop)
loop_copy = copy.deepcopy(loop)
print("ciclo preservado:", loop_copy[1] is loop_copy)
print("cópia é outro objeto:", loop_copy is not loop)

# 3) O memo é um dict {id(original): cópia}
memo: dict = {}
copy.deepcopy(box, memo)
print("entradas no memo:", len(memo))
print("tipos no memo:", sorted(type(v).__name__ for v in memo.values()))
print("chave do memo apontando p/ si mesmo:", id(memo) in memo)


# 4) __copy__ e __deepcopy__ personalizados
class Connection:
    """Guarda um recurso que não deve ser copiado (ex.: um socket)."""

    def __init__(self, url: str, history: list[str]) -> None:
        self.url = url
        self.history = history
        self.handle = object()          # recurso "caro"

    def __copy__(self):
        new = type(self).__new__(type(self))
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo):
        new = type(self).__new__(type(self))
        memo[id(self)] = new            # registra ANTES de recursar
        new.url = self.url
        new.history = copy.deepcopy(self.history, memo)
        new.handle = object()           # o clone ganha o seu recurso
        return new


conn = Connection("db://x", ["open"])
shallow = copy.copy(conn)
deep = copy.deepcopy(conn)
print("copy   compartilha handle :", shallow.handle is conn.handle)
print("deepcopy cria novo handle  :", deep.handle is not conn.handle)
print("deepcopy copia history     :", deep.history is not conn.history)
