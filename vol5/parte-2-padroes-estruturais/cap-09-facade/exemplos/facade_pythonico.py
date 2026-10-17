"""Facade em Python: uma função (ou um módulo) que esconde o roteiro de um subsistema; e as dezenas de facades que a biblioteca padrão já tem."""
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


# --- 1. a facade mais comum de Python: uma FUNÇÃO ---
def read_report(path, *, encoding="utf-8"):
    """Esconde: abrir, decodificar, ler, fechar (inclusive em caso de erro)."""
    with open(path, encoding=encoding) as f:
        return f.read()


folder = Path(tempfile.mkdtemp())
sample = folder / "a.txt"
sample.write_text("olá\n", encoding="utf-8")                    # Path.write_text é uma facade sobre open/write/close
print("Path.read_text:", repr(sample.read_text(encoding="utf-8")), "| read_report:", repr(read_report(sample)))


# --- 2. as facades da biblioteca padrão: o que cada uma esconde ---
def manual_read(path):
    f = open(path, "rb")                                        # o roteiro SEM a facade
    try:
        data = f.read()
    finally:
        f.close()
    return data.decode("utf-8")


def best(fn, n=20_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


print(f"\nPath.read_text {best(lambda: sample.read_text(encoding='utf-8')):5.1f} µs | roteiro manual {best(lambda: manual_read(sample)):5.1f} µs (da mesma ordem: a facade ainda traduz quebras de linha em modo texto, e protege do vazamento do arquivo aberto)")

result = subprocess.run([sys.executable, "-c", "print('oi')"], capture_output=True, text=True, check=True)
print("\nsubprocess.run esconde Popen + communicate + wait + o objeto de resultado:", result.stdout.strip(), "| código de saída", result.returncode)

(folder / "dados").mkdir()
(folder / "dados" / "x.txt").write_text("x", encoding="utf-8")
archive = shutil.make_archive(str(folder / "backup"), "zip", root_dir=folder / "dados")
print("shutil.make_archive esconde zipfile, a varredura de pastas e o fechamento:", Path(archive).name, f"({Path(archive).stat().st_size} bytes)")

payload = {"a": [1, 2], "b": None}
print("json.dumps é uma facade sobre JSONEncoder:", json.dumps(payload), "==", json.JSONEncoder().encode(payload))

# --- 3. a facade com SAÍDA DE EMERGÊNCIA: simples por padrão, sem trancar quem precisa de mais ---
class Archiver:
    """A porta simples: archive(pasta). As opções avançadas existem; o subsistema continua acessível."""

    def __init__(self, backend=shutil):
        self.backend = backend                                  # a saída de emergência: o subsistema é um atributo público

    def archive(self, source, target, *, fmt="zip", **options):
        return self.backend.make_archive(str(target), fmt, root_dir=source, **options)


archiver = Archiver()
simple = archiver.archive(folder / "dados", folder / "simples")
print("\nfacade simples:", Path(simple).name, "| opções avançadas passam adiante: archiver.archive(..., fmt='gztar') ->", Path(archiver.archive(folder / "dados", folder / "avancado", fmt="gztar")).name)
print("e para o que a facade não cobre, o subsistema continua ali: archiver.backend.get_archive_formats() ->", [f for f, _ in archiver.backend.get_archive_formats()][:3], "...")


# --- 4. a facade traduz os ERROS do subsistema para os do seu domínio ---
class ReportError(Exception):
    pass


def load_json_report(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ReportError(f"relatório não encontrado: {path}") from error
    except json.JSONDecodeError as error:
        raise ReportError(f"relatório inválido na linha {error.lineno}") from error


(folder / "ruim.json").write_text('{"a": 1,\n"b": }', encoding="utf-8")
for name in ("faltando.json", "ruim.json"):
    try:
        load_json_report(folder / name)
    except ReportError as error:
        print("\nerro traduzido:", error, "| causa original preservada:", type(error.__cause__).__name__)

# --- 5. a facade no nível do PACOTE: o __init__.py esconde a estrutura interna ---
print("\nno nível de um pacote, o __init__.py e o __all__ definem a porta de entrada: json.__all__ =", json.__all__)
print("quem escreve `import json; json.dumps(...)` não sabe que existem json.encoder, json.decoder e json.scanner: a estrutura interna pode mudar sem quebrar ninguém")
shutil.rmtree(folder)
