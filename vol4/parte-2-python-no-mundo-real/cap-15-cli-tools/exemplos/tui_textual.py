"""Uma interface de terminal (TUI) com o Textual, testada SEM terminal (modo headless com um 'piloto')."""
import asyncio
import tempfile
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header, Input, Static

import todo_core as core


class TodoApp(App):
    """Lista de tarefas: setas navegam, ``d`` conclui, ``n`` foca o campo de nova tarefa, ``q`` sai."""

    TITLE = "Tarefas"
    BINDINGS = [Binding("d", "done", "Concluir"), Binding("n", "new", "Nova"), Binding("q", "quit", "Sair")]

    def __init__(self, path: Path):
        super().__init__()
        self.path = path

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(cursor_type="row")
        yield Input(placeholder="nova tarefa e Enter", id="new")
        yield Static("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Feita", "Tarefa")
        self.refresh_table()

    def refresh_table(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for t in core.load(self.path):
            table.add_row(str(t.id), "x" if t.done else " ", t.text, key=str(t.id))
        self.query_one("#status", Static).update(f"{len(core.load(self.path))} tarefa(s)")

    def action_done(self) -> None:
        table = self.query_one(DataTable)
        if table.row_count:
            key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
            core.mark_done(self.path, int(key))
            self.refresh_table()

    def action_new(self) -> None:
        self.query_one("#new", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():
            core.add(self.path, event.value)
            event.input.value = ""
            self.refresh_table()
            self.query_one(DataTable).focus()


async def main() -> None:
    path = Path(tempfile.mkdtemp(prefix="tui-")) / "t.json"
    core.add(path, "Estudar Textual")
    core.add(path, "Escrever o capítulo")
    app = TodoApp(path)
    async with app.run_test(size=(80, 20)) as pilot:                   # modo headless: sem terminal, com piloto
        table = app.query_one(DataTable)
        print("linhas iniciais:", table.row_count)
        await pilot.press("d")                                         # conclui a primeira
        await pilot.press("n")                                         # foca o campo
        await pilot.press(*"Revisar", "enter")                         # digita e confirma
        await pilot.pause()
        print("depois de d, n, 'Revisar', Enter:", [(t.id, t.done, t.text) for t in core.load(path)])
        print("linhas na tela:", table.row_count, "| foco voltou à tabela?", app.focused is table)
        await pilot.press("q")
    print("app encerrou, código de saída:", app.return_code)


if __name__ == "__main__":
    asyncio.run(main())
