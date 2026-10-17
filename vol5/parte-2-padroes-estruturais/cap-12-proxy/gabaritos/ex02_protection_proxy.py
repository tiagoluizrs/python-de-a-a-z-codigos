"""Gabarito do exercício 2."""


class ProtectedProxy:
    def __init__(self, target, user, roles, rules):
        object.__setattr__(self, "_target", target)
        object.__setattr__(self, "_user", user)
        object.__setattr__(self, "_roles", set(roles))
        object.__setattr__(self, "_rules", dict(rules))
        object.__setattr__(self, "_audit", [])

    def _allowed(self, name):
        required = self._rules.get(name)
        return required is None or required in self._roles

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(f"acesso a {name} bloqueado")
        allowed = self._allowed(name)
        self._audit.append((self._user, name, "read", allowed))
        if not allowed:
            raise PermissionError(f"{self._user} não pode acessar {name}")
        return getattr(self._target, name)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            raise AttributeError(f"acesso a {name} bloqueado")
        allowed = self._allowed(name)
        self._audit.append((self._user, name, "write", allowed))
        if not allowed:
            raise PermissionError(f"{self._user} não pode alterar {name}")
        setattr(self._target, name, value)

    @property
    def audit(self):
        return list(self._audit)

    def can(self, name):
        return self._allowed(name)
