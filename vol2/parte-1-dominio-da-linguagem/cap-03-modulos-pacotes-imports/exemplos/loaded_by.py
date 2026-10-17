"""Quais modulos um unico import arrasta?"""
import sys


def snapshot() -> set[str]:
    return set(sys.modules)


before = snapshot()
import json  # noqa: E402

new = sorted(snapshot() - before)
print(len(new), new)
