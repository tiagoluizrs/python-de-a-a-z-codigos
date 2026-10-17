"""pickle executa código ao carregar. JSON só carrega dados."""
import io
import json
import pickle


class Payload:
    """Um "ataque" inofensivo: imprime um texto. Um real chamaria os.system."""

    def __reduce__(self):
        return (print, ("  >>> código executado durante pickle.loads()",))


data = pickle.dumps(Payload())
print("carregando um pickle não confiável...")
pickle.loads(data)

print("JSON com o mesmo conteúdo malicioso:", json.loads('{"__reduce__": ["print", "x"]}'))


# Mitigação parcial: um Unpickler com lista de permissão
class AllowlistUnpickler(pickle.Unpickler):
    ALLOWED = {("decimal", "Decimal")}

    def find_class(self, module, name):
        if (module, name) in self.ALLOWED:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"proibido: {module}.{name}")


def restricted_loads(raw):
    return AllowlistUnpickler(io.BytesIO(raw)).load()


from decimal import Decimal

print("dados legítimos:", restricted_loads(pickle.dumps({"a": [1, 2.5, "x"], "d": Decimal("1.5")})))
try:
    restricted_loads(data)
except pickle.UnpicklingError as error:
    print("payload bloqueado:", error)
