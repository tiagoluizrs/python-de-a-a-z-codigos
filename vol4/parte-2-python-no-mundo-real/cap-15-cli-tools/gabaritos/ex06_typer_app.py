"""Gabarito do exercício 6."""
import math
from enum import Enum
from typing import Annotated

import typer

app = typer.Typer(no_args_is_help=True)


class Mode(str, Enum):
    round = "round"
    floor = "floor"


@app.command()
def resize(
    numbers: Annotated[list[float], typer.Argument(help="números")],
    scale: Annotated[float, typer.Option("--scale", "-s", min=0)] = 1.0,
    mode: Annotated[Mode, typer.Option("--mode")] = Mode.round,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
):
    """Escala uma lista de números."""
    if verbose:
        typer.echo(f"escala={scale} modo={mode.value}")
    for x in numbers:
        value = x * scale
        typer.echo(str(math.floor(value) if mode is Mode.floor else round(value)))


@app.command()
def reset():
    """Zera."""
    typer.echo("zerado")
