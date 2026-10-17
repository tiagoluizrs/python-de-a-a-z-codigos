"""Gabarito do exercício 4."""
import difflib
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    lines: tuple = ()

    def __post_init__(self):
        object.__setattr__(self, "lines", tuple(self.lines))

    @classmethod
    def of(cls, *lines):
        return cls(lines)

    @property
    def text(self):
        return "\n".join(self.lines)

    def __len__(self):
        return len(self.lines)

    def _check(self, index, upper):
        if not 0 <= index <= upper:
            raise IndexError(f"linha fora do documento: {index}")

    def insert(self, index, text):
        self._check(index, len(self.lines))
        return Document(self.lines[:index] + (text,) + self.lines[index:])

    def delete(self, index):
        self._check(index, len(self.lines) - 1)
        return Document(self.lines[:index] + self.lines[index + 1:])

    def replace(self, index, text):
        self._check(index, len(self.lines) - 1)
        return Document(self.lines[:index] + (text,) + self.lines[index + 1:])


class Repository:
    def __init__(self):
        self._commits = {}
        self.head = Document()

    def commit(self, doc, message):
        if not isinstance(doc, Document):
            raise TypeError("só Document pode ser salvo")
        if not message.strip():
            raise ValueError("mensagem vazia")
        commit_id = len(self._commits) + 1
        self._commits[commit_id] = (message, doc)
        self.head = doc
        return commit_id

    def get(self, commit_id):
        try:
            return self._commits[commit_id][1]
        except KeyError:
            raise LookupError(f"commit desconhecido: {commit_id}") from None

    def checkout(self, commit_id):
        self.head = self.get(commit_id)
        return self.head

    def log(self):
        return [(i, message) for i, (message, _) in reversed(self._commits.items())]

    def diff(self, a_id, b_id):
        a, b = self.get(a_id).lines, self.get(b_id).lines
        removed, added = [], []
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
            if tag in ("delete", "replace"):
                removed.extend(a[i1:i2])
            if tag in ("insert", "replace"):
                added.extend(b[j1:j2])
        return {"removed": removed, "added": added}

    def shared_lines(self, a_id, b_id):
        return len({id(x) for x in self.get(a_id).lines} & {id(x) for x in self.get(b_id).lines})

    def __len__(self):
        return len(self._commits)
