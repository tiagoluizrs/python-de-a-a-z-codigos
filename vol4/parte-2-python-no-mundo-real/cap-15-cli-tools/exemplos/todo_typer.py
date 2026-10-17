"""A mesma lista de tarefas com o Typer: os TIPOS das anotações viram argumentos, validação e ajuda."""
import json
from dataclasses import asdict
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

import todo_core as core

app = typer.Typer(help="Lista de tarefas no terminal.", epilog="Arquivo: --file > $TODO_FILE > ~/.todo.json", no_args_is_help=True)


class Status(StrEnum):
    all = "all"
    open = "open"
    done = "done"


class Format(StrEnum):
    json = "json"
    csv = "csv"
    markdown = "markdown"


def version_callback(value: bool):
    if value:
        typer.echo("todo 1.0.0")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    file: Annotated[Path | None, typer.Option("--file", "-f", envvar="TODO_FILE", help="arquivo das tarefas")] = None,
    version: Annotated[bool, typer.Option("--version", callback=version_callback, is_eager=True, help="mostra a versão")] = False,
):
    ctx.obj = core.resolve_path(file)


def guarded(fn):
    """Erros de negócio -> mensagem curta em stderr e código 1 (sem traceback)."""
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except core.TodoError as error:
            typer.echo(f"todo: erro: {error}", err=True)
            raise typer.Exit(1) from None

    return wrapper


@app.command(help="adiciona uma tarefa")
@guarded
def add(ctx: typer.Context, text: str, tag: Annotated[list[str] | None, typer.Option("--tag", "-t", help="etiqueta (repita)")] = None,
        due: Annotated[str | None, typer.Option(metavar="AAAA-MM-DD", help="prazo")] = None):
    task = core.add(ctx.obj, text, tag, due)
    typer.echo(f"tarefa {task.id} criada")


@app.command(name="list", help="lista as tarefas")
@guarded
def list_(ctx: typer.Context, status: Status = Status.all, tag: str | None = None,
          as_json: Annotated[bool, typer.Option("--json", help="saída em JSON")] = False):
    tasks = core.list_tasks(ctx.obj, status.value, tag)
    if as_json:
        typer.echo(json.dumps([asdict(t) for t in tasks], ensure_ascii=False))
    else:
        for task in tasks:
            typer.echo(core.format_line(task))


@app.command(help="conclui uma tarefa")
@guarded
def done(ctx: typer.Context, id: int):
    typer.echo(f"tarefa {core.mark_done(ctx.obj, id).id} concluída")


@app.command(help="remove uma tarefa")
@guarded
def rm(ctx: typer.Context, id: int, yes: Annotated[bool, typer.Option("--yes", "-y", help="não perguntar")] = False,
       dry_run: Annotated[bool, typer.Option(help="só mostra o que faria")] = False):
    if dry_run:
        typer.echo(f"(simulação) removeria a tarefa {id}")
        return
    if not yes:
        typer.confirm(f"remover a tarefa {id}?", abort=True)
    core.remove(ctx.obj, id)
    typer.echo(f"tarefa {id} removida")


@app.command(help="exporta as tarefas")
@guarded
def export(ctx: typer.Context, fmt: Annotated[Format, typer.Option("--format")] = Format.json):
    typer.echo(core.export(ctx.obj, fmt.value))


if __name__ == "__main__":
    app()
