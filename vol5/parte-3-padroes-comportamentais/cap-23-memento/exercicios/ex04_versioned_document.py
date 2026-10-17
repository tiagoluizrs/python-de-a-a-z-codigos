"""Exercício 4: versões baratas: um documento IMUTÁVEL cujas versões compartilham as linhas que não mudaram (a ideia do ``git``)."""
import difflib
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """Um documento imutável: ``lines`` é uma TUPLA de strings (aceite qualquer iterável no construtor e converta, mesmo com a classe congelada).

    * ``Document.of(*lines)``: atalho para criar; ``text``: as linhas unidas por ``"\\n"``; ``len(doc)``: o número de linhas;
    * ``insert(index, text)``: devolve um Document NOVO com a linha inserida em ``index`` (``0 <= index <= len``, senão ``IndexError(f"linha fora do documento: {index}")``);
    * ``delete(index)`` e ``replace(index, text)``: idem (``0 <= index < len``); o original NUNCA muda;
    * as linhas que não mudaram são OS MESMOS objetos (``is``) no documento novo."""

    lines: tuple = ()

    def __post_init__(self):
        raise NotImplementedError

    @classmethod
    def of(cls, *lines: str) -> "Document":
        raise NotImplementedError

    @property
    def text(self) -> str:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def insert(self, index: int, text: str) -> "Document":
        raise NotImplementedError

    def delete(self, index: int) -> "Document":
        raise NotImplementedError

    def replace(self, index: int, text: str) -> "Document":
        raise NotImplementedError


class Repository:
    """Guarda as versões (os mementos) de um documento.

    * ``head``: o documento atual (começa como ``Document()`` vazio);
    * ``commit(doc, message)``: ``doc`` que não é um ``Document``: ``TypeError``; ``message`` vazia ou só espaços: ``ValueError("mensagem vazia")``; guarda a versão, faz dela o ``head`` e devolve o
      número do commit (1, 2, 3...);
    * ``get(commit_id)``: o documento daquele commit (``LookupError(f"commit desconhecido: {commit_id}")`` se não existe); ``checkout(commit_id)``: faz dele o ``head`` e o devolve (um ``commit`` depois
      disso cria um commit NOVO, e os antigos continuam todos lá);
    * ``log()``: lista de ``(id, message)``, do mais NOVO ao mais antigo;
    * ``diff(a_id, b_id)``: ``{"removed": [...], "added": [...]}`` usando ``difflib.SequenceMatcher(None, a.lines, b.lines).get_opcodes()``: ``removed`` são as linhas de ``a`` nos blocos
      ``delete``/``replace``; ``added`` são as linhas de ``b`` nos blocos ``insert``/``replace``, sempre na ordem em que aparecem;
    * ``shared_lines(a_id, b_id)``: quantos OBJETOS de linha (``id()``) os dois commits têm em comum;
    * ``len(repo)``: quantos commits existem."""

    def __init__(self):
        raise NotImplementedError

    def commit(self, doc: Document, message: str) -> int:
        raise NotImplementedError

    def get(self, commit_id: int) -> Document:
        raise NotImplementedError

    def checkout(self, commit_id: int) -> Document:
        raise NotImplementedError

    def log(self) -> list[tuple[int, str]]:
        raise NotImplementedError

    def diff(self, a_id: int, b_id: int) -> dict:
        raise NotImplementedError

    def shared_lines(self, a_id: int, b_id: int) -> int:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
