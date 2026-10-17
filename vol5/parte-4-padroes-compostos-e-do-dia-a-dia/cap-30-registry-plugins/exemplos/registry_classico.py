"""Registry, forma clássica: um catálogo onde as peças se registram, para o núcleo usá-las SEM conhecê-las; e as armadilhas do registro feito na importação."""
import ast
import importlib
import inspect
import sys
import tempfile
import textwrap
import time
from pathlib import Path


# --- 1. o problema: o núcleo conhece TODAS as peças ---
def export_naive(fmt, rows):
    if fmt == "csv":
        return "\n".join(",".join(map(str, r)) for r in rows)
    elif fmt == "json":
        return str([list(r) for r in rows])
    raise ValueError(f"formato desconhecido: {fmt}")


print("o núcleo com if/elif:", export_naive("csv", [(1, "a"), (2, "b")]).replace("\n", " | "), "| um formato novo ('xml') EDITA o núcleo (e todos os testes dele)")


# --- 2. o Registry: o núcleo conhece só o CATÁLOGO ---
class Registry:
    def __init__(self):
        self._items = {}

    def register(self, name, item):
        self._items[name] = item

    def get(self, name):
        try:
            return self._items[name]
        except KeyError:
            raise KeyError(f"exportador desconhecido: {name!r}; disponíveis: {', '.join(sorted(self._items)) or 'nenhum'}") from None

    def names(self):
        return sorted(self._items)


def export(registry, fmt, rows):
    return registry.get(fmt)(rows)                          # o núcleo não sabe quais formatos existem


registry = Registry()
registry.register("csv", lambda rows: "\n".join(",".join(map(str, r)) for r in rows))
registry.register("json", lambda rows: str([list(r) for r in rows]))
registry.register("xml", lambda rows: "".join(f"<row>{''.join(f'<c>{c}</c>' for c in r)}</row>" for r in rows))        # um formato novo: UMA linha, o núcleo intacto
print("\nregistry:", registry.names(), "|", export(registry, "xml", [(1, "a")]))
try:
    export(registry, "yaml", [])
except KeyError as error:
    print("pedido inválido:", error.args[0])

# --- 3. a armadilha clássica: o registro acontece NA IMPORTAÇÃO, e só se o módulo for importado ---
tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
root = Path(tmp.name)
(root / "exporters_core.py").write_text(textwrap.dedent('''
    class Registry:
        def __init__(self):
            self._items = {}

        def register(self, name, item):
            self._items[name] = item

        def get(self, name):
            try:
                return self._items[name]
            except KeyError:
                raise KeyError(f"exportador desconhecido: {name!r}; disponíveis: {', '.join(sorted(self._items)) or 'nenhum'}") from None

    registry = Registry()
'''), encoding="utf-8")
pkg = root / "exporter_plugins"
pkg.mkdir()
(pkg / "__init__.py").write_text("", encoding="utf-8")
for fmt in ("csv_out", "json_out"):
    (pkg / f"{fmt}.py").write_text(textwrap.dedent(f'''
        from exporters_core import registry

        registry.register("{fmt.split("_")[0]}", lambda rows: "{fmt}:" + str(len(rows)))     # o registro acontece quando o módulo é IMPORTADO
    '''), encoding="utf-8")
sys.path.insert(0, str(root))
core = importlib.import_module("exporters_core")
importlib.import_module("exporter_plugins.csv_out")        # o aplicativo só importou UM dos plugins
try:
    core.registry.get("json")
except KeyError as error:
    print("\nplugin json existe no disco, mas ninguém o importou:", error.args[0], "| o plugin que ninguém importa é invisível, e o erro parece um formato inexistente")

# --- 4. a gravação silenciosa por cima ---
loose = {}
loose["csv"] = lambda rows: "versão A"
loose["csv"] = lambda rows: "versão B"                      # dois plugins com o mesmo nome: o último VENCE, sem nenhum aviso
print("registro duplicado:", loose["csv"]([]), "(a versão A sumiu em silêncio; o resultado depende da ORDEM das importações)")

# --- 5. o estado global que vaza entre os testes ---
GLOBAL = Registry()


def test_one():
    GLOBAL.register("temp", lambda rows: "do teste 1")
    return GLOBAL.names()


def test_two():
    return GLOBAL.names()                                   # este teste NÃO registrou nada...


print("\nregistro global, teste 1 depois teste 2:", test_one(), test_two(), "(o teste 2 enxerga o 'temp' do teste 1: o resultado depende de quais testes rodaram antes)")


# --- 6. a cerimônia e o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nif/elif de 2 formatos:", measure([export_naive]), "| Registry + export:", measure([Registry, export]))

FORMATS = [f"fmt{i:02d}" for i in range(30)]
big = Registry()
for name in FORMATS:
    big.register(name, lambda rows: None)


def chain(fmt):
    for candidate in FORMATS:                               # o que um if/elif de 30 formatos faz: compara um por um
        if fmt == candidate:
            return candidate


def best(fn, n=200_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


print(f"achar o ÚLTIMO de 30 formatos: registro (dicionário) {best(lambda: big.get('fmt29')):4.0f} ns | if/elif em cadeia {best(lambda: chain('fmt29')):5.0f} ns")
sys.path.remove(str(root))
tmp.cleanup()
