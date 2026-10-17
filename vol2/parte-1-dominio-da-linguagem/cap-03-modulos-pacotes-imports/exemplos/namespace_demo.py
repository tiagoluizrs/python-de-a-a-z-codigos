"""Namespace package: 'acme' nao tem __init__.py e vive em 2 pastas."""
import sys
from pathlib import Path

HERE = Path(__file__).parent / "ns"
sys.path[:0] = [str(HERE / "root_a"), str(HERE / "root_b")]

import acme
import acme.billing
import acme.shipping

print(type(acme.__path__).__name__)
print([Path(p).parent.name + "/" + Path(p).name for p in acme.__path__])
print(acme.__file__, acme.__spec__.origin)
print(acme.billing.invoice(), "|", acme.shipping.ship())

import geometry
print(geometry.__file__ is not None, type(geometry.__path__).__name__)
