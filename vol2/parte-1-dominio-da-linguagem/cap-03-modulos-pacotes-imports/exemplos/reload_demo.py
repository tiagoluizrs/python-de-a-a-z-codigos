"""importlib.reload e suas armadilhas."""
import importlib
import sys
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    sys.path.insert(0, tmp)
    path = Path(tmp) / "settings_demo.py"
    path.write_text("class Config:\n    level = 1\n\nLIMIT = 10\n")

    import settings_demo
    from settings_demo import LIMIT, Config
    old_config = Config()

    path.write_text("class Config:\n    level = 2\n\nLIMIT = 100\n")
    # O mtime pode ser igual (resolucao): force a invalidacao
    importlib.invalidate_caches()
    importlib.reload(settings_demo)

    print("modulo:", settings_demo.LIMIT)          # 100
    print("from-import antigo:", LIMIT)            # 10: nome nao foi atualizado
    print("classe antiga == nova?", Config is settings_demo.Config)
    print("isinstance:", isinstance(old_config, settings_demo.Config))
    print("level antigo/novo:", Config.level, settings_demo.Config.level)
    sys.path.remove(tmp)
