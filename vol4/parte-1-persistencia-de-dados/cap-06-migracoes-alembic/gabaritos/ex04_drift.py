"""Gabarito do exercício 4."""
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext


class DriftError(AssertionError):
    def __init__(self, differences):
        super().__init__("deriva entre modelo e banco: " + "; ".join(differences))
        self.differences = differences


def _flatten(diffs):
    for diff in diffs:
        if isinstance(diff, list):
            yield from _flatten(diff)
        else:
            yield diff


def schema_drift(engine, metadata):
    with engine.connect() as conn:
        context = MigrationContext.configure(conn, opts={"compare_type": True})
        diffs = list(_flatten(compare_metadata(context, metadata)))
    out = []
    for diff in diffs:
        kind = diff[0]
        if kind == "add_table":
            out.append(f"add_table:{diff[1].name}")
        elif kind == "remove_table":
            if diff[1].name != "alembic_version":
                out.append(f"remove_table:{diff[1].name}")
        elif kind == "add_column":
            out.append(f"add_column:{diff[2]}.{diff[3].name}")
        elif kind == "remove_column":
            out.append(f"remove_column:{diff[2]}.{diff[3].name}")
        elif kind == "modify_type":
            out.append(f"modify_type:{diff[2]}.{diff[3]}")
        elif kind == "modify_nullable":
            out.append(f"modify_nullable:{diff[2]}.{diff[3]}")
    return sorted(out)


def assert_in_sync(engine, metadata):
    differences = schema_drift(engine, metadata)
    if differences:
        raise DriftError(differences)
