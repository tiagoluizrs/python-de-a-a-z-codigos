"""A mesma lista de tarefas com o Click: decoradores em vez de um parser montado à mão."""
import json
import sys
from dataclasses import asdict

import click

import todo_core as core


class TodoGroup(click.Group):
    """Traduz os erros de negócio em mensagem curta e código de saída 1."""

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except core.TodoError as error:
            click.echo(f"todo: erro: {error}", err=True)
            ctx.exit(1)


@click.group(cls=TodoGroup, help="Lista de tarefas no terminal.", epilog="Arquivo: --file > $TODO_FILE > ~/.todo.json")
@click.version_option("1.0.0", prog_name="todo")
@click.option("-f", "--file", "file", type=click.Path(path_type=str), envvar="TODO_FILE", help="arquivo das tarefas")
@click.pass_context
def cli(ctx, file):
    ctx.obj = core.resolve_path(file)


@cli.command(help="adiciona uma tarefa")
@click.argument("text")
@click.option("-t", "--tag", multiple=True, help="etiqueta (repita para várias)")
@click.option("--due", metavar="AAAA-MM-DD", help="prazo")
@click.pass_obj
def add(path, text, tag, due):
    task = core.add(path, text, list(tag), due)
    click.echo(f"tarefa {task.id} criada")


@cli.command(name="list", help="lista as tarefas")
@click.option("--status", type=click.Choice(["all", "open", "done"]), default="all", show_default=True)
@click.option("--tag", help="só desta etiqueta")
@click.option("--json", "as_json", is_flag=True, help="saída em JSON")
@click.pass_obj
def list_(path, status, tag, as_json):
    tasks = core.list_tasks(path, status, tag)
    if as_json:
        click.echo(json.dumps([asdict(t) for t in tasks], ensure_ascii=False))
    else:
        for task in tasks:
            click.echo(core.format_line(task))


@cli.command(help="conclui uma tarefa")
@click.argument("id", type=int)
@click.pass_obj
def done(path, id):
    click.echo(f"tarefa {core.mark_done(path, id).id} concluída")


@cli.command(help="remove uma tarefa (pede confirmação)")
@click.argument("id", type=int)
@click.option("--yes", "-y", is_flag=True, help="não perguntar")
@click.option("--dry-run/--no-dry-run", default=False, help="só mostra o que faria")
@click.pass_obj
def rm(path, id, yes, dry_run):
    if dry_run:
        click.echo(f"(simulação) removeria a tarefa {id}")
        return
    if not yes:
        click.confirm(f"remover a tarefa {id}?", abort=True)             # abort=True: responder 'n' sai com código 1
    core.remove(path, id)
    click.echo(f"tarefa {id} removida")


@cli.command(help="exporta as tarefas")
@click.option("--format", "fmt", type=click.Choice(["json", "csv", "markdown"]), default="json", show_default=True)
@click.pass_obj
def export(path, fmt):
    click.echo(core.export(path, fmt))


if __name__ == "__main__":
    sys.exit(cli())
