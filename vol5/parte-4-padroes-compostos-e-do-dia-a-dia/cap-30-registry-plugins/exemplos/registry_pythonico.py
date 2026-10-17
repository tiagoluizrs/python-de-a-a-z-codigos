"""Registry e plugins em Python: decorador, __init_subclass__, descoberta por pacote (pkgutil), entry points (importlib.metadata) e carga preguiçosa."""
import importlib
import importlib.metadata
import pkgutil
import sys
import tempfile
import textwrap
import time
import types
from abc import ABC
from pathlib import Path


# --- 1. o registro por DECORADOR ---
class Registry:
    def __init__(self, kind="plugin"):
        self.kind, self._items = kind, {}

    def register(self, name, *, replace=False):
        def decorator(obj):
            key = name.strip().lower()
            if key in self._items and not replace:
                raise ValueError(f"{self.kind} já registrado: {key}")        # falha ALTO: nada de "o último vence"
            self._items[key] = obj
            return obj                                                        # devolve o objeto: a função continua utilizável
        return decorator

    def get(self, name):
        try:
            return self._items[name.strip().lower()]
        except KeyError:
            raise KeyError(f"{self.kind} desconhecido: {name!r}; disponíveis: {', '.join(sorted(self._items)) or 'nenhum'}") from None

    def names(self):
        return sorted(self._items)


exporters = Registry("exportador")


@exporters.register("csv")
def to_csv(rows):
    return "\n".join(",".join(map(str, r)) for r in rows)


@exporters.register("json")
def to_json(rows):
    return str([list(r) for r in rows])


print("decorador:", exporters.names(), "|", exporters.get("CSV")([(1, "a")]), "| to_csv continua uma função normal:", to_csv([(2, "b")]))
try:
    @exporters.register("csv")
    def other_csv(rows):
        return "outro"
except ValueError as error:
    print("duplicado:", error, "(o registro por decorador acontece quando o módulo é importado, e a colisão aparece NA HORA, não em produção)")


# --- 2. o registro automático por __init_subclass__ ---
class Exporter:
    registry = {}
    extension = ""

    def __init_subclass__(cls, name=None, abstract=False, **kwargs):
        super().__init_subclass__(**kwargs)
        if abstract:
            return                                                            # classes intermediárias não entram no catálogo
        key = (name or cls.__name__.removesuffix("Exporter")).lower()
        if key in Exporter.registry:
            raise ValueError(f"exportador já registrado: {key}")
        Exporter.registry[key] = cls

    def export(self, rows):
        raise NotImplementedError


class TextExporter(Exporter, abstract=True):
    separator = ","

    def export(self, rows):
        return "\n".join(self.separator.join(map(str, r)) for r in rows)


class CsvExporter(TextExporter):                                              # registrada como "csv", sem NENHUMA linha de registro
    extension = ".csv"


class TabExporter(TextExporter, name="tabs"):
    separator = "\t"
    extension = ".tsv"


print("\n__init_subclass__:", sorted(Exporter.registry), "| a intermediária 'TextExporter' (abstract=True) ficou de fora |", Exporter.registry["tabs"]().export([(1, "a")]).replace("\t", "<TAB>"))

# --- 3. a descoberta por pacote: o núcleo NÃO importa os plugins um por um ---
tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
root = Path(tmp.name)
pkg = root / "exporter_plugins_demo"
pkg.mkdir()
(pkg / "__init__.py").write_text("", encoding="utf-8")
PLUGINS = {
    "csv_out": 'NAME = "csv"\nAPI_VERSION = 2\n\ndef run(rows):\n    return "csv"\n',
    "json_out": 'NAME = "json"\nAPI_VERSION = 2\n\ndef run(rows):\n    return "json"\n',
    "old_api": 'NAME = "legacy"\nAPI_VERSION = 1\n\ndef run(rows):\n    return "legacy"\n',
    "broken": "import modulo_que_nao_existe_xyz\n",
    "_helpers": "NAME = 'não é plugin'\n",
}
for module, code in PLUGINS.items():
    (pkg / f"{module}.py").write_text(code, encoding="utf-8")
sys.path.insert(0, str(root))
SUPPORTED_API = 2


def discover(package_name):
    package = importlib.import_module(package_name)
    plugins, errors = {}, {}
    for info in pkgutil.iter_modules(package.__path__):
        if info.name.startswith("_"):
            continue
        try:
            module = importlib.import_module(f"{package_name}.{info.name}")
        except Exception as error:                                            # um plugin quebrado NÃO derruba o aplicativo
            errors[info.name] = f"{type(error).__name__}: {error}"
            continue
        if getattr(module, "API_VERSION", None) != SUPPORTED_API:
            errors[info.name] = f"versão de API não suportada: {getattr(module, 'API_VERSION', None)}"
            continue
        plugins[module.NAME] = module
    return plugins, errors


found, problems = discover("exporter_plugins_demo")
print("\ndescoberta por pacote:", sorted(found), "| problemas isolados:", problems)

# --- 4. os entry points: plugins de OUTROS pacotes instalados ---
dist = root / "demo_plugin-1.0.dist-info"
dist.mkdir()
(dist / "METADATA").write_text("Metadata-Version: 2.1\nName: demo-plugin\nVersion: 1.0\n", encoding="utf-8")
(dist / "entry_points.txt").write_text("[demo.exporters]\nyaml = demo_plugin_mod:YamlExporter\nbroken = demo_plugin_mod:DoesNotExist\n", encoding="utf-8")
(root / "demo_plugin_mod.py").write_text("class YamlExporter:\n    extension = '.yaml'\n", encoding="utf-8")
importlib.invalidate_caches()
loaded = {}
for entry in sorted(importlib.metadata.entry_points(group="demo.exporters"), key=lambda e: e.name):
    try:
        loaded[entry.name] = entry.load()
    except Exception as error:
        loaded[entry.name] = f"{type(error).__name__}: {error}"
print("entry points do grupo 'demo.exporters':", {k: (v.__name__ if isinstance(v, type) else v) for k, v in loaded.items()})
print("(quem instala o pacote 'demo-plugin' acrescenta um exportador SEM editar o núcleo; ele precisa só declarar o grupo no pyproject.toml)")


# --- 5. a carga preguiçosa: o registro guarda o CAMINHO, não o módulo ---
class LazyRegistry:
    def __init__(self):
        self._targets, self._loaded = {}, {}

    def register(self, name, target):
        self._targets[name] = target                                          # "modulo:atributo" (texto) ou o próprio objeto

    def get(self, name):
        if name not in self._loaded:
            target = self._targets[name]
            if isinstance(target, str):
                module_name, _, attribute = target.partition(":")
                target = getattr(importlib.import_module(module_name), attribute)         # só AGORA o módulo é importado
            self._loaded[name] = target
        return self._loaded[name]

    def loaded(self):
        return sorted(self._loaded)


lazy = LazyRegistry()
lazy.register("rgb", "colorsys:rgb_to_hsv")
lazy.register("frac", "fractions:Fraction")
print("\ncarga preguiçosa: antes do get, colorsys importado?", "colorsys" in sys.modules, end=" | ")
hsv = lazy.get("rgb")(1, 0, 0)
print("depois:", "colorsys" in sys.modules, "| 'fractions' continua de fora?", "frac" not in lazy.loaded(), "| carregados:", lazy.loaded(), hsv)

for i in range(20):
    (root / f"lazy_plugin_{i:02d}.py").write_text("DATA = [n * n for n in range(30_000)]\n\nclass Plugin:\n    pass\n", encoding="utf-8")


def ms(fn):
    start = time.perf_counter()
    fn()
    return (time.perf_counter() - start) * 1000


eager = ms(lambda: [importlib.import_module(f"lazy_plugin_{i:02d}") for i in range(20)])
for i in range(20, 40):
    (root / f"lazy_plugin_{i:02d}.py").write_text("DATA = [n * n for n in range(30_000)]\n\nclass Plugin:\n    pass\n", encoding="utf-8")
on_demand = LazyRegistry()
for i in range(20, 40):
    on_demand.register(f"p{i}", f"lazy_plugin_{i:02d}:Plugin")
lazy_cost = ms(lambda: on_demand.get("p20"))
print(f"20 plugins com trabalho na importação | carregar todos na partida {eager:6.1f} ms | registrar os caminhos e usar 1 sob demanda {lazy_cost:5.2f} ms")

# --- 6. outros "registros" que a linguagem já tem ---
class Sink(ABC):
    pass


Sink.register(list)                                                           # uma subclasse VIRTUAL: o registro de uma ABC
print("\nABC.register(list):", isinstance([], Sink), "| e functools.singledispatch.register (Capítulos 15 e 24) é um registro por TIPO")


# --- 7. o custo ---
def build(n, registered):
    Base = Exporter if registered else object
    for i in range(n):
        kwargs = {"name": f"gen{i}_{registered}_{time.perf_counter_ns()}"} if registered else {}
        types.new_class(f"C{i}", (Base,), kwargs)


def fastest(registered, repeats=7):
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        build(2_000, registered)
        times.append((time.perf_counter() - start) * 1000)
    return min(times)


plain, registered_cost = fastest(False), fastest(True)
start = time.perf_counter()
importlib.metadata.entry_points(group="demo.exporters")
discovery = (time.perf_counter() - start) * 1000
print(f"criar 2.000 classes: sem registro {plain:5.1f} ms | com __init_subclass__ {registered_cost:5.1f} ms | listar os entry points de TODOS os pacotes instalados: {discovery:5.1f} ms (uma vez, na partida)")
sys.path.remove(str(root))
tmp.cleanup()
