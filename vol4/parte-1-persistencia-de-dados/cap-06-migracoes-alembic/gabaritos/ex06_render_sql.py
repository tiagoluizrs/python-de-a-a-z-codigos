"""Gabarito do exercício 6."""
import io
import re
from collections import Counter

from alembic import command


def render_sql(config, start="base", end="head"):
    previous = config.output_buffer
    buffer = io.StringIO()
    config.output_buffer = buffer
    try:
        command.upgrade(config, f"{start}:{end}", sql=True)
    finally:
        config.output_buffer = previous
    return buffer.getvalue()


def summarize_sql(sql):
    lines = [line for line in sql.splitlines() if line.strip() and not line.strip().startswith("--")]
    counts = Counter()
    for statement in " ".join(lines).split(";"):
        match = re.match(r"\s*([A-Za-z]+)", statement)
        if match:
            counts[match.group(1).upper()] += 1
    return dict(counts)
