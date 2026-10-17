"""Exceções próprias: hierarquia, atributos e o problema do pickle."""
import pickle


class AppError(Exception):
    """Base de todos os erros do domínio: quem usa a biblioteca captura só esta."""


class ValidationError(AppError):
    def __init__(self, field, message):
        super().__init__(field, message)         # args = (field, message)
        self.field = field
        self.message = message

    def __str__(self):
        return f"{self.field}: {self.message}"


try:
    raise ValidationError("email", "formato inválido")
except AppError as error:
    print(type(error).__name__, "|", error, "|", error.args)


# Pegadinha: um __init__ com assinatura própria quebra o pickle
class BadError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")   # args tem UM elemento
        self.code = code


try:
    pickle.loads(pickle.dumps(BadError(404, "x")))
except TypeError as error:
    print("pickle falhou:", error)

restored = pickle.loads(pickle.dumps(ValidationError("nome", "vazio")))
print("pickle ok:", restored.field, restored.message, restored.args)

# Detalhes do str/repr das exceções
print(str(KeyError("chave")), "|", str(ValueError("chave")))
print(repr(ValueError("a", 1)), ValueError().args)
