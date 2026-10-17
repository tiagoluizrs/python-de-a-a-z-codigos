"""Gabarito do exercício 4."""
import csv
import json

import click


@click.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option("--column", "-c", required=True, help="coluna numérica")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
@click.option("--skip-invalid", is_flag=True, help="ignora valores que não são números")
def stats(file, column, fmt, skip_invalid):
    """Estatísticas de uma coluna numérica de um CSV."""
    with open(file, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if column not in (reader.fieldnames or []):
            raise click.ClickException(f"coluna {column!r} não existe (colunas: {', '.join(reader.fieldnames or [])})")
        values = []
        for number, row in enumerate(reader, start=2):
            text = row[column]
            try:
                values.append(float(text))
            except (TypeError, ValueError):
                if not skip_invalid:
                    raise click.ClickException(f"linha {number}: valor inválido {text!r}") from None
    if not values:
        raise click.ClickException("nenhum valor numérico")
    result = {"n": len(values), "min": min(values), "max": max(values), "mean": sum(values) / len(values)}
    if fmt == "json":
        click.echo(json.dumps(result))
    else:
        for key, value in result.items():
            click.echo(f"{key}={value}")
