"""Saída bonita e útil com o Rich: tabelas, progresso, painéis e rastros de erro (e o custo de cada um)."""
import io
import logging
import time

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, track
from rich.table import Table
from rich.traceback import Traceback

import todo_core as core

# 1. o Console decide sozinho: em um terminal, cor e largura; em um pipe/arquivo, texto limpo
for label, console in [("terminal (forçado)", Console(file=io.StringIO(), force_terminal=True, width=60, color_system="standard")),
                       ("arquivo/pipe", Console(file=io.StringIO(), force_terminal=False, width=60))]:
    console.print("[bold green]ok[/] 3 tarefas")
    print(f"{label:<20} é terminal? {console.is_terminal!s:<5} | saída: {console.file.getvalue()!r}")

# 2. tabela: colunas alinhadas, largura ajustada, estilo por coluna
tasks = [core.Task(1, "Comprar café", True, ["casa"], "2026-11-01"), core.Task(2, "Estudar Python 3.15", False, ["estudo", "python"], None),
         core.Task(3, "Revisar o capítulo de CLIs com um texto bem comprido para quebrar a linha", False, [], "2026-12-31")]
table = Table(title="Tarefas", show_lines=False)
table.add_column("ID", justify="right", style="cyan")
table.add_column("Feita", justify="center")
table.add_column("Tarefa", overflow="fold")
table.add_column("Etiquetas", style="magenta")
for t in tasks:
    table.add_row(str(t.id), "✔" if t.done else "·", t.text, ", ".join(t.tags))
console = Console(record=True, file=io.StringIO(), width=70, force_terminal=False)
console.print(table)
print(console.export_text())

# 3. painel e erros: a mensagem de erro com contexto
console = Console(record=True, file=io.StringIO(), width=60, force_terminal=False)
console.print(Panel("o arquivo de tarefas está corrompido\n[dim]/home/ana/.todo.json[/]", title="erro", border_style="red"))
print(console.export_text())

# 4. um rastro de erro legível (rich.traceback) em vez do traceback padrão
try:
    core.mark_done(core.resolve_path("/nao/existe/t.json"), 7)
except core.TodoError as error:
    console = Console(record=True, file=io.StringIO(), width=80, force_terminal=False)
    console.print(Traceback.from_exception(type(error), error, error.__traceback__, show_locals=False, max_frames=3))
    lines = [l for l in console.export_text().splitlines() if l.strip()]
    print(f"traceback do Rich: {len(lines)} linhas com o código-fonte de cada quadro | última: {lines[-1]!r}")

# 5. barra de progresso: só aparece em terminal, e não suja arquivos de log
console = Console(file=io.StringIO(), force_terminal=False)
for _ in track(range(1000), description="processando", console=console):
    pass
print("\nprogresso sem terminal -> saída (sem animação):", repr(console.file.getvalue()[:60]))
with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=Console(file=io.StringIO(), force_terminal=False)) as progress:
    job = progress.add_task("baixando", total=100)
    progress.update(job, advance=100)
    print("tarefa concluída?", progress.tasks[0].finished)

# 6. logging com o RichHandler: níveis coloridos, tempo e local do código
log_console = Console(record=True, file=io.StringIO(), width=90, force_terminal=False)
logging.basicConfig(level="INFO", handlers=[RichHandler(console=log_console, show_path=False, show_time=False, rich_tracebacks=True)], format="%(message)s", force=True)
logging.getLogger("todo").info("carregadas %d tarefas", 3)
logging.getLogger("todo").warning("arquivo sem prazo em %d tarefas", 2)
print("\nlog:", [line.strip()[:70] for line in log_console.export_text().splitlines() if line.strip()])

# 7. o preço: imprimir 20.000 linhas
N = 20_000
buffer = io.StringIO()
start = time.perf_counter()
for i in range(N):
    print(f"tarefa {i}", file=buffer)
t_print = (time.perf_counter() - start) * 1e3
console = Console(file=io.StringIO(), force_terminal=True, width=80)
start = time.perf_counter()
for i in range(N):
    console.print(f"tarefa [bold]{i}[/]")
t_rich = (time.perf_counter() - start) * 1e3
big = Table()
big.add_column("n")
for i in range(N):
    big.add_row(str(i))
console = Console(file=io.StringIO(), force_terminal=True, width=80)
start = time.perf_counter()
console.print(big)
t_table = (time.perf_counter() - start) * 1e3
print(f"\n{N:,} linhas: print {t_print:6.1f} ms | console.print com markup {t_rich:7.1f} ms ({t_rich / t_print:.0f}x) | uma Table de {N:,} linhas {t_table:7.1f} ms")
print("(Rich é para PESSOAS: para um milhão de linhas que outro programa lê, use print/JSON; e nunca imprima uma tabela gigante)")
