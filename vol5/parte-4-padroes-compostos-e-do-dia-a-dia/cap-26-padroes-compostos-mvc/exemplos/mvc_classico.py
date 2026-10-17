"""MVC clássico: vários padrões trabalhando juntos: Observer (modelo -> visões), Command (controlador traduz entrada em chamadas) e Memento (desfazer)."""
import ast
import inspect
import textwrap
import time


# --- 1. o problema: tudo em uma função (dados, entrada e tela misturados) ---
def god_app(lines):
    items, screens = [], []
    for line in lines:
        cmd, _, arg = line.partition(" ")
        if cmd == "add":
            items.append([arg, False])
        elif cmd == "done":
            items[int(arg) - 1][1] = True
        elif cmd == "rm":
            items.pop(int(arg) - 1)
        screens.append(" | ".join(f"[{'x' if done else ' '}] {text}" for text, done in items))     # a tela dentro da lógica
    return screens


print("tudo em um lugar:", god_app(["add leite", "add pão", "done 1"])[-1], "| para testar a regra 'done', é preciso rodar a entrada e a tela; uma segunda tela (contador) edita o laço")


# --- 2. o MVC: três papéis, cada um com UMA razão para mudar ---
class Model:
    """O estado e as regras. NÃO conhece as visões: só avisa quem se inscreveu (Observer)."""

    def __init__(self):
        self.items = []                                     # [texto, feito]
        self._observers = []
        self._batch = 0
        self._dirty = False

    def subscribe(self, observer):
        self._observers.append(observer)

    def _notify(self):
        if self._batch:
            self._dirty = True                              # dentro de um lote: avisa UMA vez no fim
            return
        for observer in self._observers:
            observer.update(self)

    def batch(self):
        return _Batch(self)

    def add(self, text):
        self.items.append([text, False])
        self._notify()

    def toggle(self, index):
        self.items[index][1] = not self.items[index][1]
        self._notify()

    def remove(self, index):
        del self.items[index]
        self._notify()

    def snapshot(self):                                     # o Memento: copia as listas de dentro
        return [list(item) for item in self.items]

    def restore(self, snapshot):
        self.items = [list(item) for item in snapshot]
        self._notify()


class _Batch:
    def __init__(self, model):
        self.model = model

    def __enter__(self):
        self.model._batch += 1

    def __exit__(self, *exc):
        self.model._batch -= 1
        if not self.model._batch and self.model._dirty:
            self.model._dirty = False
            self.model._notify()


class TextView:
    """Uma visão: só MOSTRA. Não altera o modelo e não decide nada."""

    def __init__(self, model, out):
        self.out = out
        model.subscribe(self)

    def update(self, model):
        self.out.append(" | ".join(f"[{'x' if done else ' '}] {text}" for text, done in model.items))


class CountView:
    def __init__(self, model, out):
        self.out = out
        model.subscribe(self)

    def update(self, model):
        self.out.append(f"{sum(done for _, done in model.items)}/{len(model.items)} feitas")


class Controller:
    """Traduz a ENTRADA (texto) em chamadas ao modelo; guarda o histórico para desfazer."""

    def __init__(self, model):
        self.model, self.history = model, []

    def handle(self, line):
        cmd, _, arg = line.partition(" ")
        if cmd == "undo":
            if self.history:
                self.model.restore(self.history.pop())
            return
        before = self.model.snapshot()
        match cmd:
            case "add":
                self.model.add(arg)
            case "done":
                self.model.toggle(int(arg) - 1)
            case "rm":
                self.model.remove(int(arg) - 1)
            case _:
                raise ValueError(f"comando desconhecido: {cmd}")
        self.history.append(before)


model, text_out, count_out = Model(), [], []
TextView(model, text_out)
CountView(model, count_out)
controller = Controller(model)
for line in ("add leite", "add pão", "done 1", "rm 2", "undo"):
    controller.handle(line)
print("\nTextView:", text_out[-1], "| CountView:", count_out[-1], "(depois de 'undo', o pão voltou)")
print("o modelo sozinho (sem visão, sem controlador):", end=" ")
solo = Model()
solo.add("teste")
solo.toggle(0)
print(solo.items, "| a regra é testável sem tela e sem entrada")


# --- 3. uma visão nova NÃO edita o modelo nem o controlador ---
class JsonView:
    def __init__(self, model, out):
        self.out = out
        model.subscribe(self)

    def update(self, model):
        self.out.append([{"text": t, "done": d} for t, d in model.items])


json_out = []
JsonView(model, json_out)
controller.handle("add café")
print("\nvisão nova (8 linhas, nenhuma edição no resto):", json_out[-1])
try:
    controller.handle("fly")
except ValueError as error:
    print("entrada inválida chega como erro do controlador:", error, "| histórico intacto:", len(controller.history))


# --- 4. a tempestade de notificações ---
class CountingView:
    def __init__(self, model):
        self.updates = 0
        model.subscribe(self)

    def update(self, model):
        self.updates += 1


storm = Model()
view = CountingView(storm)
for i in range(1_000):
    storm.add(f"tarefa {i}")
print(f"\nimportar 1.000 tarefas uma a uma: {view.updates} atualizações da visão", end=" | ")
lot = Model()
view = CountingView(lot)
with lot.batch():
    for i in range(1_000):
        lot.add(f"tarefa {i}")
print(f"em lote: {view.updates} atualização")


# --- 5. a cerimônia e o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\ntudo em uma função:", measure([god_app]), "| MVC (Model + _Batch + TextView + Controller):", measure([Model, _Batch, TextView, Controller]))


def best(fn, n=20_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


m = Model()
TextView(m, [])
CountView(m, [])
c = Controller(m)
c.handle("add x")
print(f"alternar uma tarefa com 2 visões inscritas: {best(lambda: m.toggle(0)):5.2f} µs | o mesmo pelo controlador (com snapshot): {best(lambda: c.handle('done 1')):5.2f} µs")
