"""Checklist de compatibilidade com o free-threading (rode nos dois builds)."""
import importlib
import sys
import sysconfig
import warnings

STDLIB = ["json", "re", "sqlite3", "ssl", "zlib", "hashlib", "decimal", "asyncio", "multiprocessing", "ctypes", "socket", "datetime", "collections", "itertools"]


def main():
    print("build free-threaded:", bool(sysconfig.get_config_var("Py_GIL_DISABLED")), "| GIL ativo:", sys._is_gil_enabled())
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for name in STDLIB:
            importlib.import_module(name)
    print(f"depois de importar {len(STDLIB)} módulos da biblioteca padrão: GIL ativo =", sys._is_gil_enabled(), "| avisos:", len(caught))
    print("sufixo de extensão C deste build:", sysconfig.get_config_var("EXT_SUFFIX"))
    print("flags: thread_inherit_context =", sys.flags.thread_inherit_context, "| context_aware_warnings =", getattr(sys.flags, "context_aware_warnings", "n/d"))


if __name__ == "__main__":
    main()
