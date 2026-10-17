"""Gabarito do exercício 1."""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str = ""


SECRETS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(password|senha|secret|api[_-]?key|token)\s*=\s*['\"][^'\"\s]{6,}['\"]"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def _name(path):
    return path.rsplit("/", 1)[-1]


def scan_project(files):
    out = []
    pyproject = files.get("pyproject.toml")
    if pyproject is None or "requires-python" not in pyproject:
        out.append(Finding("PR001", "erro", "pyproject.toml ausente ou sem requires-python"))
    names = {_name(p) for p in files}
    has_lock = bool(names & {"uv.lock", "poetry.lock", "pdm.lock", "Pipfile.lock"})
    pinned = any(re.fullmatch(r"requirements.*\.txt", _name(p)) and "==" in c for p, c in files.items())
    if not has_lock and not pinned:
        out.append(Finding("PR002", "erro", "sem lock nem requirements com versões fixas"))
    if not any((_name(p).startswith("test_") and _name(p).endswith(".py")) or _name(p).endswith("_test.py") for p in files):
        out.append(Finding("PR003", "erro", "nenhum arquivo de teste"))
    if ".env" in files:
        out.append(Finding("PR006", "erro", ".env presente"))
    elif ".gitignore" in files and not any(line.startswith(".env") for line in files[".gitignore"].splitlines()):
        out.append(Finding("PR006", "aviso", ".gitignore não ignora .env"))
    for path, content in files.items():
        if path.endswith((".py", ".yaml", ".yml", ".toml", ".json", ".cfg", ".ini")) and any(p.search(content) for p in SECRETS):
            out.append(Finding("PR007", "erro", f"possível segredo em {path}"))
    return sorted(out, key=lambda f: (f.severity != "erro", f.rule))


def scan_dockerfile(text):
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
    out, stages = [], set()
    kinds = [l.split(None, 1)[0].upper() for l in lines]
    if "USER" not in kinds:
        out.append(Finding("PR004", "erro", "sem USER"))
    if "HEALTHCHECK" not in kinds:
        out.append(Finding("PR004", "aviso", "sem HEALTHCHECK"))
    for line in lines:
        parts = line.split()
        word = parts[0].upper()
        if word == "FROM":
            image = parts[1]
            if "AS" in [p.upper() for p in parts]:
                stages.add(parts[[p.upper() for p in parts].index("AS") + 1].lower())
            tag = image.rsplit("/", 1)[-1]
            if image.lower() != "scratch" and image.lower() not in stages and "@sha256:" not in image and (":" not in tag or tag.endswith(":latest")):
                out.append(Finding("PR004", "erro", f"imagem sem versão fixa: {image}"))
        elif word in ("ENV", "ARG"):
            name = re.split(r"[= ]", line.split(None, 1)[1], maxsplit=1)[0] if len(parts) > 1 else ""
            if re.search(r"(?i)PASSWORD|SECRET|TOKEN|KEY", name):
                out.append(Finding("PR004", "erro", f"segredo em {word} {name}"))
    return out


def score(findings):
    return max(0, 100 - 15 * sum(f.severity == "erro" for f in findings) - 5 * sum(f.severity == "aviso" for f in findings))


def render(findings):
    errors = sum(f.severity == "erro" for f in findings)
    warnings = len(findings) - errors
    lines = [f"[{f.severity:<5}] {f.rule} {f.message}".rstrip() for f in findings]
    lines.append(f"placar: {score(findings)}/100 ({errors} erros, {warnings} avisos)")
    return "\n".join(lines)
