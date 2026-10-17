"""Gabarito do exercício 5."""
import inspect


def signature_report(func):
    report = []
    for param in inspect.signature(func).parameters.values():
        # Parameter.empty é o marcador de "sem valor padrão"
        has_default = param.default is not inspect.Parameter.empty
        report.append((param.name, param.kind.name, has_default))
    return report
