"""Gabarito do exercício 1."""
import sys
import sysconfig


def detect_runtime():
    free_threaded_build = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
    check = getattr(sys, "_is_gil_enabled", None)
    gil_enabled = check() if check else True
    return {
        "free_threaded_build": free_threaded_build,
        "gil_enabled": gil_enabled,
        "parallel_threads": free_threaded_build and not gil_enabled,
        "version": (sys.version_info.major, sys.version_info.minor),
    }


def describe_runtime(info):
    major, minor = info["version"]
    if not info["free_threaded_build"]:
        kind = "build com GIL"
    elif info["gil_enabled"]:
        kind = "build sem GIL, GIL religado"
    else:
        kind = "build sem GIL, GIL desligado"
    return f"Python {major}.{minor} ({kind})"
