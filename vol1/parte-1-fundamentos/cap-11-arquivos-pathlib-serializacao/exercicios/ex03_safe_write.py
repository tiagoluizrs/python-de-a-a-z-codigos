"""Exercício 3: escrita atômica de arquivos."""
from pathlib import Path


def safe_write(path: Path, data: str | bytes) -> None:
    """Grave ``data`` em ``path`` de forma atômica.

    Regras:
    - ``str`` é gravada em UTF-8 sem tradução de quebras de linha;
      ``bytes`` é gravado como está. Outro tipo levanta ``TypeError``.
    - Escreva em um arquivo temporário NO MESMO diretório de ``path``
      (``tempfile.mkstemp(dir=...)``), force a gravação com ``flush`` e
      ``os.fsync`` e troque com ``os.replace``.
    - Se qualquer passo falhar, o arquivo original permanece intacto
      (ou continua inexistente) e o temporário é removido.
    - Ao final com sucesso, não pode sobrar nenhum arquivo temporário.
    """
    raise NotImplementedError
