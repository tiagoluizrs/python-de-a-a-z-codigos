"""Um importador minimo em sys.meta_path (didatico)."""
import importlib.abc
import importlib.util
import sys

VIRTUAL = {
    "virtual_config": "DEBUG = True\nNAME = 'in-memory'\n",
    "virtual_math": "def triple(x):\n    return 3 * x\n",
}


class StringImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Finder e loader no mesmo objeto: modulos vindos de um dict."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname in VIRTUAL:
            return importlib.util.spec_from_loader(fullname, self)
        return None            # nao e comigo: o proximo finder tenta

    def create_module(self, spec):
        return None            # usa a criacao padrao de modulo

    def exec_module(self, module):
        exec(VIRTUAL[module.__name__], module.__dict__)


sys.meta_path.insert(0, StringImporter())

import virtual_config
from virtual_math import triple

print(virtual_config.NAME, triple(7))
print(virtual_config.__spec__.loader.__class__.__name__)
print(hasattr(virtual_config, "__file__"))
print([type(f).__name__ if not isinstance(f, type) else f.__name__
       for f in sys.meta_path])
