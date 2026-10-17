"""Gabarito do exercício 1."""
import platform


def describe_runtime() -> dict[str, str]:
    return {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
    }
