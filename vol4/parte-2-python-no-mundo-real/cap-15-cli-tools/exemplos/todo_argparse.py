"""A lista de tarefas com a biblioteca padrão (argparse): zero dependências."""
import argparse
import json
import sys
from dataclasses import asdict

import todo_core as core

__version__ = "1.0.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="Lista de tarefas no terminal.",
                                     epilog="Arquivo: --file > $TODO_FILE > ~/.todo.json")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-f", "--file", help="arquivo das tarefas (padrão: $TODO_FILE ou ~/.todo.json)")
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMANDO")

    add = sub.add_parser("add", help="adiciona uma tarefa")
    add.add_argument("text", help="o que fazer")
    add.add_argument("-t", "--tag", action="append", default=[], help="etiqueta (repita para várias)")
    add.add_argument("--due", metavar="AAAA-MM-DD", help="prazo")

    ls = sub.add_parser("list", help="lista as tarefas")
    ls.add_argument("--status", choices=["all", "open", "done"], default="all")
    ls.add_argument("--tag", help="só desta etiqueta")
    ls.add_argument("--json", action="store_true", help="saída em JSON (para outros programas)")

    done = sub.add_parser("done", help="conclui uma tarefa")
    done.add_argument("id", type=int)

    rm = sub.add_parser("rm", help="remove uma tarefa")
    rm.add_argument("id", type=int)
    rm.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=False, help="só mostra o que faria")

    exp = sub.add_parser("export", help="exporta as tarefas")
    exp.add_argument("--format", dest="fmt", choices=["json", "csv", "markdown"], default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = core.resolve_path(args.file)
    try:
        if args.command == "add":
            task = core.add(path, args.text, args.tag, args.due)
            print(f"tarefa {task.id} criada")
        elif args.command == "list":
            tasks = core.list_tasks(path, args.status, args.tag)
            if args.json:
                print(json.dumps([asdict(t) for t in tasks], ensure_ascii=False))
            else:
                for task in tasks:
                    print(core.format_line(task))
        elif args.command == "done":
            print(f"tarefa {core.mark_done(path, args.id).id} concluída")
        elif args.command == "rm":
            if args.dry_run:
                print(f"(simulação) removeria a tarefa {args.id}")
            else:
                core.remove(path, args.id)
                print(f"tarefa {args.id} removida")
        elif args.command == "export":
            print(core.export(path, args.fmt))
    except core.TodoError as error:
        print(f"todo: erro: {error}", file=sys.stderr)                # erros vão para STDERR, resultados para STDOUT
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
