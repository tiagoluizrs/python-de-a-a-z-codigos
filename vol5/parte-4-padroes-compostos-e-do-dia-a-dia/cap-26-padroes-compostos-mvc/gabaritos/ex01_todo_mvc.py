"""Gabarito do exercício 1."""


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


class Model:
    def __init__(self):
        self._items = []
        self._observers = []
        self._batch = 0
        self._dirty = False

    @property
    def items(self):
        return [(text, done) for text, done in self._items]

    def subscribe(self, observer):
        self._observers.append(observer)

    def unsubscribe(self, observer):
        if observer not in self._observers:
            raise ValueError("não inscrito")
        self._observers.remove(observer)

    def _notify(self):
        if self._batch:
            self._dirty = True
            return
        for observer in list(self._observers):
            observer.update(self)

    def _check(self, index):
        if not 0 <= index < len(self._items):
            raise IndexError(f"tarefa inexistente: {index}")

    def add(self, text):
        if not text.strip():
            raise ValueError("texto vazio")
        self._items.append([text.strip(), False])
        self._notify()

    def toggle(self, index):
        self._check(index)
        self._items[index][1] = not self._items[index][1]
        self._notify()

    def remove(self, index):
        self._check(index)
        del self._items[index]
        self._notify()

    def snapshot(self):
        return [list(item) for item in self._items]

    def restore(self, snapshot):
        self._items = [list(item) for item in snapshot]
        self._notify()

    def batch(self):
        return _Batch(self)


class TextView:
    def __init__(self, model, out):
        self.out = out
        model.subscribe(self)

    def update(self, model):
        items = model.items
        self.out.append(" | ".join(f"[{'x' if done else ' '}] {text}" for text, done in items) if items else "(vazio)")


class StatsView:
    def __init__(self, model, out):
        self.out = out
        model.subscribe(self)

    def update(self, model):
        items = model.items
        self.out.append(f"{sum(done for _, done in items)}/{len(items)} feitas")


class Controller:
    def __init__(self, model):
        self.model = model
        self._undo, self._redo = [], []

    def _number(self, arg):
        try:
            n = int(arg)
        except ValueError:
            raise ValueError(f"número inválido: {arg}") from None
        if not 1 <= n <= len(self.model.items):
            raise IndexError(f"tarefa inexistente: {n}")
        return n - 1

    def _change(self, action):
        before = self.model.snapshot()
        action()
        self._undo.append(before)
        self._redo.clear()

    def handle(self, line):
        cmd, _, arg = line.strip().partition(" ")
        arg = arg.strip()
        match cmd:
            case "add":
                self._change(lambda: self.model.add(arg))
            case "done":
                index = self._number(arg)
                self._change(lambda: self.model.toggle(index))
            case "rm":
                index = self._number(arg)
                self._change(lambda: self.model.remove(index))
            case "clear":
                done = [i for i, (_, d) in enumerate(self.model.items) if d]
                if not done:
                    return

                def clear():
                    with self.model.batch():
                        for i in reversed(done):
                            self.model.remove(i)

                self._change(clear)
            case "undo":
                if not self._undo:
                    raise LookupError("nada para desfazer")
                self._redo.append(self.model.snapshot())
                self.model.restore(self._undo.pop())
            case "redo":
                if not self._redo:
                    raise LookupError("nada para refazer")
                self._undo.append(self.model.snapshot())
                self.model.restore(self._redo.pop())
            case _:
                raise ValueError(f"comando desconhecido: {cmd}")
