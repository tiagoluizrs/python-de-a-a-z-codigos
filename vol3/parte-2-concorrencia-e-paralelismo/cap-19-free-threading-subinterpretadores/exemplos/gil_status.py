"""Em qual Python estou? Build, GIL e como mudar."""
import subprocess
import sys
import sysconfig

import builds


def describe():
    free_threaded_build = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
    gil_enabled = sys._is_gil_enabled()
    return {
        "versao": sys.version.split()[0],
        "build_free_threaded": free_threaded_build,
        "gil_ativo_agora": gil_enabled,
        "sufixo_de_extensao": sysconfig.get_config_var("EXT_SUFFIX"),
    }


if __name__ == "__main__":
    print("este interpretador:", describe())
    code = "import sys, sysconfig; print(bool(sysconfig.get_config_var('Py_GIL_DISABLED')), sys._is_gil_enabled(), sysconfig.get_config_var('EXT_SUFFIX'))"
    print(f"{'build':<18}{'free-threaded?':<16}{'GIL ativo?':<12}sufixo de extensão")
    for label, python in builds.builds():
        if python:
            free, gil, suffix = builds.run_code(python, code).split()
            print(f"{label:<18}{free:<16}{gil:<12}{suffix}")

    # ligar o GIL de volta no build sem GIL
    t = builds.find_python("3.15+freethreaded")
    if t:
        for how, args, env in (("-X gil=1", ["-X", "gil=1"], None), ("PYTHON_GIL=1", [], {"PYTHON_GIL": "1"})):
            import os
            out = subprocess.run([t, *args, "-c", "import sys; print(sys._is_gil_enabled())"], capture_output=True, text=True, env={**os.environ, **(env or {})}).stdout.strip()
            print(f"build sem GIL com {how:<13}: GIL ativo = {out}")
