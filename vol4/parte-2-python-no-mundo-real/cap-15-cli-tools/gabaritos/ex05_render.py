"""Gabarito do exercício 5."""
import csv
import io
import json

from rich.console import Console
from rich.table import Table


def render(rows, fmt, color=False, width=80):
    if fmt == "json":
        return json.dumps(rows, ensure_ascii=False)
    if fmt == "csv":
        out = io.StringIO()
        if rows:
            writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        return out.getvalue().rstrip("\n")
    if fmt == "plain":
        return "\n".join("\t".join(str(v) for v in row.values()) for row in rows)
    if fmt == "table":
        if not rows:
            return "(vazio)"
        table = Table(show_header=True, header_style="bold" if color else "")
        for key in rows[0]:
            table.add_column(str(key))
        for row in rows:
            table.add_row(*[str(v) for v in row.values()])
        buffer = io.StringIO()
        Console(file=buffer, force_terminal=color, color_system="standard" if color else None, width=width).print(table)
        return buffer.getvalue().rstrip("\n")
    raise ValueError(f"formato desconhecido: {fmt!r}")


def want_color(mode, is_tty, env):
    if mode == "always":
        return True
    if mode == "never":
        return False
    if mode == "auto":
        return bool(is_tty) and "NO_COLOR" not in env
    raise ValueError(f"modo de cor desconhecido: {mode!r}")
