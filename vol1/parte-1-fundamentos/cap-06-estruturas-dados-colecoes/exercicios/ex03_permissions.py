"""Exercício 3: auditoria de permissões com álgebra de conjuntos."""


def audit(granted: set[str], used: set[str]) -> dict[str, set[str]]:
    """Compare as permissões concedidas a um usuário com as realmente usadas.

    Devolva um dict com três conjuntos:

    - ``"unused"``: concedidas e nunca usadas (candidatas a revogação);
    - ``"missing"``: usadas sem terem sido concedidas (alerta!);
    - ``"active"``: concedidas e usadas.

    ``audit({"read", "write", "admin"}, {"read", "delete"})`` devolve
    ``{"unused": {"write", "admin"}, "missing": {"delete"},
    "active": {"read"}}``.
    """
    raise NotImplementedError
