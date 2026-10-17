"""Três jeitos de testar um comando, e quanto custa cada um."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from click.testing import CliRunner as ClickRunner
from typer.testing import CliRunner as TyperRunner

import todo_argparse
import todo_click
import todo_typer

HERE = Path(__file__).parent
store = Path(tempfile.mkdtemp(prefix="cli-test-")) / "t.json"


def fresh():
    store.unlink(missing_ok=True)


# 1. em processo, argparse: main(argv) devolve o código; capture stdout/stderr com contextlib
fresh()
out, err = io.StringIO(), io.StringIO()
with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
    code = todo_argparse.main(["-f", str(store), "add", "Escrever testes", "-t", "qa"])
    code2 = todo_argparse.main(["-f", str(store), "done", "99"])
print(f"argparse  : código {code} e {code2} | stdout {out.getvalue()!r} | stderr {err.getvalue()!r}")

# argparse chama sys.exit(2) em uso incorreto: capture SystemExit
with contextlib.redirect_stderr(io.StringIO()):
    try:
        todo_argparse.main(["-f", str(store), "list", "--status", "talvez"])
    except SystemExit as exit_:
        print("uso incorreto levanta SystemExit com código", exit_.code)

# 2. em processo, Click e Typer: o CliRunner captura saída, código e exceção, e simula a entrada
fresh()
result = ClickRunner().invoke(todo_click.cli, ["-f", str(store), "add", "Escrever testes", "-t", "qa"])
print(f"\nClick     : código {result.exit_code} | saída {result.output!r}")
result = ClickRunner().invoke(todo_click.cli, ["-f", str(store), "rm", "1"], input="n\n")
print(f"Click rm  : respondeu 'n' -> código {result.exit_code} | saída {result.output!r}")
result = ClickRunner().invoke(todo_click.cli, ["-f", str(store), "rm", "1"], input="y\n")
print(f"Click rm  : respondeu 'y' -> {result.output.splitlines()[-1]!r} | código {result.exit_code}")

fresh()
result = TyperRunner().invoke(todo_typer.app, ["add", "Escrever testes"], env={"TODO_FILE": str(store)})
print(f"\nTyper     : código {result.exit_code} | saída {result.output!r} (a variável de ambiente entrou em `env=`)")
result = TyperRunner().invoke(todo_typer.app, ["list", "--status", "talvez"], env={"TODO_FILE": str(store)})
print(f"Typer erro: código {result.exit_code} (uso incorreto) | menciona 'talvez'? {'talvez' in result.output}")

# 3. de fora, como um usuário: subprocess (o único teste que pega o ponto de entrada e a instalação de verdade)
fresh()
with contextlib.redirect_stdout(io.StringIO()):
    todo_argparse.main(["-f", str(store), "add", "Escrever testes"])
proc = subprocess.run([sys.executable, str(HERE / "todo_argparse.py"), "-f", str(store), "list"], capture_output=True, text=True)
print(f"\nsubprocess: código {proc.returncode} | saída {proc.stdout!r}")

# 4. o custo de cada abordagem (100 execuções do mesmo comando `list`)
fresh()
with contextlib.redirect_stdout(io.StringIO()):
    todo_argparse.main(["-f", str(store), "add", "x"])


def best(fn, n):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e3


def argparse_inproc():
    with contextlib.redirect_stdout(io.StringIO()):
        todo_argparse.main(["-f", str(store), "list"])


def click_inproc():
    ClickRunner().invoke(todo_click.cli, ["-f", str(store), "list"])


def subprocess_run():
    subprocess.run([sys.executable, str(HERE / "todo_argparse.py"), "-f", str(store), "list"], capture_output=True)


t_a, t_c, t_s = best(argparse_inproc, 200), best(click_inproc, 200), best(subprocess_run, 10)
print(f"\ncusto por teste: argparse em processo {t_a:6.2f} ms | CliRunner (Click) {t_c:6.2f} ms | subprocess {t_s:7.1f} ms ({t_s / t_a:,.0f}x)")
print("(teste a LÓGICA em processo, aos milhares; use poucos testes de subprocess para o ponto de entrada)")

# 5. a variável de ambiente e o diretório de trabalho: isole cada teste (monkeypatch no pytest)
os.environ["TODO_FILE"] = str(store)
print("\nTODO_FILE definido no processo -> resolve_path(None):", todo_argparse.core.resolve_path(None) == store)
