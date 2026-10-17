"""Leitura de arquivo com tratamento de erros (versão robusta do capítulo)."""
from pathlib import Path


def read_text_file(path: str) -> str:
    try:
        # O context manager fecha o arquivo mesmo se ocorrer erro
        with open(path, encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}") from None


if __name__ == "__main__":
    print(read_text_file(str(Path(__file__))))
