"""Gabarito do exercício 1."""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    rule: str
    line: int
    message: str


INSTALL = re.compile(r"(pip install|uv sync|npm install|poetry install|apt-get install)")
SECRET_NAME = re.compile(r"PASSWORD|SECRET|TOKEN|KEY", re.IGNORECASE)


def _instructions(text):
    """(linha, INSTRUÇÃO, argumento) com as continuações já juntas."""
    out, buffer, start = [], "", 0
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not buffer and (not stripped or stripped.startswith("#")):
            continue
        if stripped.startswith("#") and buffer:
            continue                                            # comentário no meio de uma continuação
        if not buffer:
            start = number
        if stripped.endswith("\\"):
            buffer += stripped[:-1].strip() + " "
            continue
        full = (buffer + stripped).strip()
        buffer = ""
        word, _, arg = full.partition(" ")
        out.append((start, word.upper(), arg.strip()))
    if buffer:
        word, _, arg = buffer.strip().partition(" ")
        out.append((start, word.upper(), arg.strip()))
    return out


def lint(dockerfile):
    items = _instructions(dockerfile)
    findings = []
    stages = set()
    last_from = None
    has_user = has_health = False
    saw_broad_copy = None
    for line, word, arg in items:
        if word == "FROM":
            last_from = line
            parts = arg.split()
            image = parts[0] if parts else ""
            if "AS" in [p.upper() for p in parts]:
                stages.add(parts[[p.upper() for p in parts].index("AS") + 1].lower())
            if image.lower() != "scratch" and image.lower() not in stages and "@sha256:" not in image:
                name = image.rsplit("/", 1)[-1]
                if ":" not in name or name.endswith(":latest"):
                    findings.append(Finding("DL001", line, f"imagem base sem versão fixa: {image}"))
        elif word == "USER":
            has_user = True
        elif word == "HEALTHCHECK":
            has_health = True
        elif word in ("CMD", "ENTRYPOINT") and not arg.startswith("["):
            findings.append(Finding("DL003", line, f"{word} em forma shell: use a forma exec (lista JSON)"))
        elif word == "COPY":
            tokens = [t for t in arg.split() if not t.startswith("--")]
            if len(tokens) >= 2 and tokens[0] == "." and saw_broad_copy is None:
                saw_broad_copy = line
        elif word == "ADD":
            tokens = [t for t in arg.split() if not t.startswith("--")]
            if tokens and not tokens[0].startswith(("http://", "https://")):
                findings.append(Finding("DL007", line, "use COPY em vez de ADD para arquivos locais"))
        elif word in ("ENV", "ARG"):
            name = re.split(r"[= ]", arg, maxsplit=1)[0]
            if SECRET_NAME.search(name):
                findings.append(Finding("DL008", line, f"{word} {name}: o valor fica gravado na imagem"))
        elif word == "RUN":
            if INSTALL.search(arg) and saw_broad_copy is not None and not any(f.rule == "DL004" for f in findings):
                findings.append(Finding("DL004", saw_broad_copy, "COPY . antes da instalação de dependências: invalida o cache"))
            if "pip install" in arg and "--no-cache-dir" not in arg and "type=cache" not in arg:
                findings.append(Finding("DL005", line, "pip install sem --no-cache-dir"))
            if "apt-get install" in arg and ("--no-install-recommends" not in arg or "rm -rf /var/lib/apt/lists" not in arg):
                findings.append(Finding("DL006", line, "apt-get install sem --no-install-recommends ou sem limpar /var/lib/apt/lists"))
    if last_from is None:
        return []
    if not has_user:
        findings.append(Finding("DL002", last_from, "nenhum USER: o processo roda como root"))
    if not has_health:
        findings.append(Finding("DL009", last_from, "sem HEALTHCHECK"))
    return sorted(findings, key=lambda f: (f.line, f.rule))
