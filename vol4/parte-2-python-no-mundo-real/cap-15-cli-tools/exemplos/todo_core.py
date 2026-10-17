"""O NÚCLEO de uma lista de tarefas: sem argparse, sem click, sem print.

As três interfaces (argparse, Click e Typer) são só cascas finas sobre este módulo: a lógica fica testável sem terminal.
"""
import csv
import io
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

DEFAULT_FILE = Path.home() / ".todo.json"


class TodoError(Exception):
    """Erro de negócio (mostrado ao usuário em uma linha, sem traceback)."""


@dataclass
class Task:
    id: int
    text: str
    done: bool = False
    tags: list[str] = field(default_factory=list)
    due: str | None = None


def resolve_path(flag: str | Path | None = None) -> Path:
    """Precedência: flag > variável de ambiente TODO_FILE > padrão (a regra do Capítulo 12 do Volume 3)."""
    if flag:
        return Path(flag)
    env = os.environ.get("TODO_FILE")
    return Path(env) if env else DEFAULT_FILE


def load(path: Path) -> list[Task]:
    if not path.exists():
        return []
    try:
        return [Task(**item) for item in json.loads(path.read_text(encoding="utf-8"))]
    except (json.JSONDecodeError, TypeError) as error:
        raise TodoError(f"arquivo de tarefas corrompido ({path}): {error}") from error


def save(path: Path, tasks: list[Task]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps([asdict(t) for t in tasks], ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)                                      # troca atômica: nunca deixa um arquivo pela metade


def add(path: Path, text: str, tags: list[str] | None = None, due: str | None = None) -> Task:
    text = text.strip()
    if not text:
        raise TodoError("o texto da tarefa não pode ser vazio")
    if due is not None:
        try:
            date.fromisoformat(due)
        except ValueError:
            raise TodoError(f"data inválida {due!r}: use AAAA-MM-DD") from None
    tasks = load(path)
    task = Task(id=max((t.id for t in tasks), default=0) + 1, text=text, tags=sorted(set(tags or [])), due=due)
    save(path, tasks + [task])
    return task


def list_tasks(path: Path, status: str = "all", tag: str | None = None) -> list[Task]:
    tasks = load(path)
    if status == "open":
        tasks = [t for t in tasks if not t.done]
    elif status == "done":
        tasks = [t for t in tasks if t.done]
    if tag:
        tasks = [t for t in tasks if tag in t.tags]
    return tasks


def mark_done(path: Path, task_id: int) -> Task:
    tasks = load(path)
    for task in tasks:
        if task.id == task_id:
            task.done = True
            save(path, tasks)
            return task
    raise TodoError(f"tarefa {task_id} não existe")


def remove(path: Path, task_id: int) -> None:
    tasks = load(path)
    kept = [t for t in tasks if t.id != task_id]
    if len(kept) == len(tasks):
        raise TodoError(f"tarefa {task_id} não existe")
    save(path, kept)


def export(path: Path, fmt: str = "json") -> str:
    tasks = load(path)
    if fmt == "json":
        return json.dumps([asdict(t) for t in tasks], ensure_ascii=False, indent=2)
    if fmt == "csv":
        out = io.StringIO()
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(["id", "text", "done", "tags", "due"])
        for t in tasks:
            writer.writerow([t.id, t.text, t.done, ";".join(t.tags), t.due or ""])
        return out.getvalue()
    if fmt == "markdown":
        return "\n".join(f"- [{'x' if t.done else ' '}] {t.text}" + (f" (até {t.due})" if t.due else "") for t in tasks)
    raise TodoError(f"formato desconhecido: {fmt!r} (use json, csv ou markdown)")


def format_line(t: Task) -> str:
    box = "x" if t.done else " "
    tags = " " + " ".join(f"#{tag}" for tag in t.tags) if t.tags else ""
    due = f" (até {t.due})" if t.due else ""
    return f"[{box}] {t.id:>3}  {t.text}{tags}{due}"
