"""Gabarito do exercício 3."""


def _check_slo(slo):
    if not 0 < slo < 1:
        raise ValueError("slo deve estar entre 0 e 1 (exclusive)")


def error_budget(total, slo):
    _check_slo(slo)
    if total < 0:
        raise ValueError("total negativo")
    return total * (1 - slo)


def budget_spent(bad, total, slo):
    if total == 0:
        _check_slo(slo)
        return 0.0
    return bad / error_budget(total, slo)


def burn_rate(bad, total, slo):
    _check_slo(slo)
    if bad < 0 or total < 0 or bad > total:
        raise ValueError("valores inválidos")
    if total == 0:
        return 0.0
    return (bad / total) / (1 - slo)


def days_to_exhaustion(rate, window_days=30.0):
    return window_days / rate if rate > 0 else float("inf")


def should_page(windows, slo, threshold=14.4):
    if not windows:
        raise ValueError("é preciso ao menos uma janela")
    return all(burn_rate(bad, total, slo) >= threshold for bad, total in windows)


def allowed_downtime_minutes(slo, window_days=30.0):
    _check_slo(slo)
    return window_days * 24 * 60 * (1 - slo)
