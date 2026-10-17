"""Um verificador de PRONTIDÃO PARA PRODUÇÃO: as lições do volume, como regras sobre os arquivos de um projeto.

O núcleo é uma função pura: ``scan({caminho: conteúdo}) -> [Finding]``. Quem lê o disco é ``readiness.py``.
"""
import re
from dataclasses import dataclass

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),                                              # chave de acesso AWS
    re.compile(r"(?i)(password|senha|secret|api[_-]?key|token)\s*=\s*['\"][^'\"\s]{6,}['\"]"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str            # "erro" | "aviso"
    message: str
    path: str = ""


def _is_source(path: str) -> bool:
    return path.endswith(".py") and not path.startswith(("tests/", "test_")) and "/tests/" not in path and "test_" not in path.rsplit("/", 1)[-1]


def scan(files: dict[str, str]) -> list[Finding]:
    """Aplica as regras. ``files`` mapeia caminho relativo (com ``/``) -> conteúdo de texto."""
    findings: list[Finding] = []
    names = set(files)
    sources = {p: c for p, c in files.items() if _is_source(p)}

    # PR001: metadados e versão do Python (Capítulos 1 e 11 do Volume 3)
    pyproject = files.get("pyproject.toml")
    if pyproject is None:
        findings.append(Finding("PR001", "erro", "não há pyproject.toml"))
    elif "requires-python" not in pyproject:
        findings.append(Finding("PR001", "erro", "pyproject.toml sem requires-python", "pyproject.toml"))

    # PR002: dependências travadas (Capítulo 2 do Volume 3): build reproduzível
    if not names & {"uv.lock", "poetry.lock", "pdm.lock", "Pipfile.lock"}:
        pinned = [p for p, c in files.items() if re.fullmatch(r"requirements.*\.txt", p) and "==" in c]
        if not pinned:
            findings.append(Finding("PR002", "erro", "nenhum arquivo de lock (uv.lock...) nem requirements com versões fixas"))

    # PR003: testes (Capítulo 4 do Volume 3)
    if not any(re.search(r"(^|/)(test_[^/]+|[^/]+_test)\.py$", p) for p in names):
        findings.append(Finding("PR003", "erro", "nenhum arquivo de teste (test_*.py)"))

    # PR004: Dockerfile seguro (Capítulo 17)
    docker = files.get("Dockerfile")
    if docker is not None:
        lines = [l.strip() for l in docker.splitlines() if l.strip() and not l.strip().startswith("#")]
        if not any(l.upper().startswith("USER ") for l in lines):
            findings.append(Finding("PR004", "erro", "Dockerfile sem USER: o processo roda como root", "Dockerfile"))
        if not any(l.upper().startswith("HEALTHCHECK") for l in lines):
            findings.append(Finding("PR004", "aviso", "Dockerfile sem HEALTHCHECK", "Dockerfile"))
        for l in lines:
            if l.upper().startswith("FROM ") and (re.search(r":latest(\s|$)", l) or not re.search(r"[:@]", l.split()[1])) and l.split()[1].lower() != "scratch" \
                    and l.split()[1] not in {m.group(1) for m in re.finditer(r"(?i)\bAS\s+(\S+)", docker)}:
                findings.append(Finding("PR004", "erro", f"imagem base sem versão fixa: {l.split()[1]}", "Dockerfile"))
        if any(re.match(r"(?i)^(ENV|ARG)\s+\w*(PASSWORD|SECRET|TOKEN|KEY)\w*[= ]", l) for l in lines):
            findings.append(Finding("PR004", "erro", "segredo em ENV/ARG do Dockerfile (fica gravado na imagem)", "Dockerfile"))
        if ".dockerignore" not in names:
            findings.append(Finding("PR005", "erro", "há Dockerfile, mas não há .dockerignore (o contexto leva .git e .env)"))

    # PR006: o .env não pode ser versionado (Capítulo 12 do Volume 3)
    gitignore = files.get(".gitignore", "")
    if ".env" in names:
        findings.append(Finding("PR006", "erro", ".env presente no projeto (segredos versionados)", ".env"))
    elif ".gitignore" in names and not re.search(r"(?m)^\.env\b", gitignore):
        findings.append(Finding("PR006", "aviso", ".gitignore não ignora .env", ".gitignore"))

    # PR007: segredos no código (Capítulo 8 do Volume 3)
    for path, content in files.items():
        if path.endswith((".py", ".yaml", ".yml", ".toml", ".json", ".cfg", ".ini")):
            if any(p.search(content) for p in SECRET_PATTERNS):
                findings.append(Finding("PR007", "erro", "possível segredo no código ou na configuração", path))

    # PR008: saúde e logging (Capítulos 3 (Vol. 3) e 16)
    code = "\n".join(sources.values())
    if sources and not re.search(r"/health|/healthz|/livez|/readyz", code) and not any("compose" in p for p in names):
        findings.append(Finding("PR008", "aviso", "nenhuma rota de saúde (/healthz) encontrada no código"))
    if sources and not re.search(r"\blogging\b|structlog|loguru", code):
        findings.append(Finding("PR008", "aviso", "o código não usa logging (só print?)"))
    prints = sum(len(re.findall(r"(?m)^\s*print\(", c)) for p, c in sources.items() if not p.startswith(("exemplos/", "scripts/")))
    if prints > 10:
        findings.append(Finding("PR008", "aviso", f"{prints} chamadas de print() em código de aplicação: use logging"))

    # PR009: README e licença (Capítulo 10 do Volume 3)
    if not any(p.lower().startswith("readme") for p in names):
        findings.append(Finding("PR009", "aviso", "não há README"))

    # PR010: tipagem (Capítulo 6 do Volume 3)
    if sources and "py.typed" not in " ".join(names) and not re.search(r"\bmypy\b|\bpyright\b|\bty\b", files.get("pyproject.toml", "") + "".join(v for k, v in files.items() if k.endswith((".yaml", ".yml", ".cfg", ".ini")))):
        findings.append(Finding("PR010", "aviso", "nenhum verificador de tipos configurado (mypy, pyright)"))

    return sorted(findings, key=lambda f: (f.severity != "erro", f.rule, f.path, f.message))


def score(findings: list[Finding]) -> int:
    """0 a 100: cada erro tira 15 pontos e cada aviso, 5 (mínimo 0)."""
    return max(0, 100 - 15 * sum(f.severity == "erro" for f in findings) - 5 * sum(f.severity == "aviso" for f in findings))
