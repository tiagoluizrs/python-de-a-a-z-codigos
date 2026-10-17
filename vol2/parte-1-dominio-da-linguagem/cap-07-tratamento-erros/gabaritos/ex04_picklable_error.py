"""Gabarito do exercício 4."""


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(status, message)     # args = (status, message): o pickle reconstrói
        self.status = status
        self.message = message

    def __str__(self):
        return f"{self.status}: {self.message}"


class NotFound(ApiError):
    def __init__(self, message):
        super().__init__(404, message)

    def __reduce__(self):
        # O padrão chamaria NotFound(404, message), que não existe: diga como reconstruir
        return (type(self), (self.message,))
