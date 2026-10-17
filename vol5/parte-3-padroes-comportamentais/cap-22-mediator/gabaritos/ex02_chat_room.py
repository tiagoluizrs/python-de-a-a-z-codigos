"""Gabarito do exercício 2."""


class ChatRoom:
    def __init__(self):
        self._members = {}
        self._muted = set()
        self._banned = []
        self._history = []

    def _check(self, name):
        if name not in self._members:
            raise LookupError(f"usuário desconhecido: {name}")

    def join(self, name, deliver):
        if not callable(deliver):
            raise TypeError("deliver precisa ser chamável")
        if name in self._members:
            raise ValueError(f"nome já em uso: {name}")
        self._members[name] = deliver

    def leave(self, name):
        self._check(name)
        del self._members[name]
        self._muted = {(by, who) for by, who in self._muted if name not in (by, who)}

    def members(self):
        return sorted(self._members)

    def mute(self, by, who):
        self._check(by)
        self._check(who)
        if by == who:
            raise ValueError("não pode silenciar a si mesmo")
        self._muted.add((by, who))

    def unmute(self, by, who):
        self._muted.discard((by, who))

    def ban_word(self, word):
        self._banned.append(word.lower())

    def send(self, sender, text, to=None):
        self._check(sender)
        if to is not None:
            self._check(to)
        for word in text.split():
            cleaned = word.strip(".,;:!?").lower()
            if cleaned in self._banned:
                raise ValueError(f"palavra proibida: {cleaned}")
        self._history.append((sender, to, text))
        targets = [to] if to is not None else [n for n in self._members if n != sender]
        delivered = 0
        for name in targets:
            if name == sender or (name, sender) in self._muted:
                continue
            self._members[name](sender, text, to is not None)
            delivered += 1
        return delivered

    @property
    def history(self):
        return list(self._history)
