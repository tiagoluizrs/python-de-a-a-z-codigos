"""Roda o verificador de prontidão sobre um projeto de verdade (pasta) e imprime o placar.

    python exemplos/readiness.py                       # os projetos dos capítulos 17 e 18, e um projeto 'ruim' de brinquedo
    python exemplos/readiness.py CAMINHO/DO/PROJETO
"""
import sys
import tempfile
from pathlib import Path

from readiness_core import Finding, score, scan

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache", "saida", "_book"}


def read_project(root: Path, limit: int = 2000) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if len(files) >= limit:
            break
        rel = path.relative_to(root)
        if path.is_file() and not (set(rel.parts) & SKIP_DIRS):
            try:
                files[rel.as_posix()] = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                files[rel.as_posix()] = ""                          # binário: só a existência importa
    return files


def report(title: str, files: dict[str, str]) -> None:
    findings = scan(files)
    print(f"\n{title}: {len(files)} arquivos | placar {score(findings)}/100 | {sum(f.severity == 'erro' for f in findings)} erros, {sum(f.severity == 'aviso' for f in findings)} avisos")
    for f in findings:
        print(f"  [{f.severity:>5}] {f.rule} {f.message}" + (f"  ({f.path})" if f.path else ""))
    if not findings:
        print("  nada a apontar")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        report(sys.argv[1], read_project(Path(sys.argv[1])))
    else:
        here = Path(__file__).resolve()
        part7 = here.parents[2]
        for label, rel in [("Cap. 17, o serviço com o Dockerfile de produção", "cap-17-dockerizacao/exemplos/app"), ("Cap. 18, o pacote em camadas", "cap-18-arquitetura-projeto")]:
            report(label, read_project(part7 / rel))
        bad = {
            "app.py": "import os\nPASSWORD = 'hunter2hunter2'\nprint('oi')\n" * 3,
            "requirements.txt": "flask\nrequests\n",
            "Dockerfile": "FROM python\nCOPY . .\nENV API_TOKEN=abc123\nCMD python app.py\n",
            ".env": "DB_URL=postgres://u:p@h/db\n",
        }
        report("um projeto 'ruim' de brinquedo", bad)
