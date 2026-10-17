"""Gabarito do exercício 4."""


class LoginPresenter:
    def __init__(self, view, auth, max_attempts=3):
        self.view, self.auth, self.max_attempts = view, auth, max_attempts
        self._failures = 0
        self._blocked = False

    def on_input_changed(self, field):
        self.view.clear_error(field)

    def reset(self):
        self._failures, self._blocked = 0, False

    @property
    def failures(self):
        return self._failures

    @property
    def blocked(self):
        return self._blocked

    def _validate(self, username, password):
        errors = []
        name = username.strip()
        if not name:
            errors.append(("username", "informe o usuário"))
        elif len(name) < 3:
            errors.append(("username", "mínimo de 3 caracteres"))
        if not password:
            errors.append(("password", "informe a senha"))
        elif len(password) < 8:
            errors.append(("password", "mínimo de 8 caracteres"))
        return errors

    def on_submit(self, username, password):
        if self._blocked:
            self.view.clear_errors()
            self.view.show_error("form", "conta bloqueada")
            return False
        self.view.clear_errors()
        errors = self._validate(username, password)
        if errors:
            for field, message in errors:
                self.view.show_error(field, message)
            return False
        self.view.set_busy(True)
        offline = False
        try:
            name = self.auth(username.strip().lower(), password)
        except ConnectionError:
            name, offline = None, True
        finally:
            self.view.set_busy(False)                        # SEMPRE, e ANTES de qualquer mensagem
        if offline:
            self.view.show_error("form", "sem conexão, tente de novo")
            return False
        if name is None:
            self._failures += 1
            if self._failures >= self.max_attempts:
                self._blocked = True
                self.view.show_error("form", "conta bloqueada")
            else:
                self.view.show_error("form", "usuário ou senha inválidos")
            return False
        self._failures = 0
        self.view.show_success(name)
        return True
