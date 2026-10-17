"""Exercício 4: o arquivo RECORD de uma wheel."""
import zipfile


def record_line(path, data):
    """``"caminho,sha256=<hash>,<tamanho>"``: o hash é o SHA-256 em base64
    URL-safe SEM o preenchimento ``=`` (``base64.urlsafe_b64encode(...).rstrip(b"=")``)
    e o tamanho é ``len(data)``."""
    raise NotImplementedError


def make_record(files, record_path):
    """Conteúdo do RECORD para o dict ``files`` (``{caminho: bytes}``), uma linha por
    arquivo em ORDEM ALFABÉTICA do caminho, mais a linha do próprio RECORD
    (``"<record_path>,,"``) por ÚLTIMO. Termina com ``"\\n"``."""
    raise NotImplementedError


def verify_wheel(zip_path):
    """Confere uma wheel (``.whl`` é um zip) contra o RECORD (o único arquivo
    ``*.dist-info/RECORD``). Devolve a lista ORDENADA de problemas, no formato
    ``"hash:<caminho>"`` (hash ou tamanho divergente), ``"missing:<caminho>"``
    (listado no RECORD e ausente do zip) e ``"extra:<caminho>"`` (presente no zip
    e ausente do RECORD, exceto o próprio RECORD e entradas de diretório).
    Wheel íntegra: ``[]``. Sem RECORD, levanta ``ValueError``."""
    raise NotImplementedError
