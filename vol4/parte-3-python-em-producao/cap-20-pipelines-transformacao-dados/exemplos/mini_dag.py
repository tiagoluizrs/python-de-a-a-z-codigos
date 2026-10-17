"""Um orquestrador de DAG em ~100 linhas: ordem topológica, paralelismo por ondas, novas tentativas, cache por conteúdo e recomeço."""
import hashlib
import inspect
import json
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Task:
    name: str
    fn: callable
    deps: list[str] = field(default_factory=list)
    retries: int = 0


class Pipeline:
    def __init__(self, tasks: list[Task], cache_dir: Path, workers: int = 4):
        self.tasks = {t.name: t for t in tasks}
        self.cache_dir, self.workers = cache_dir, workers
        self.log: list[tuple[str, str, float]] = []
        self._lock = threading.Lock()

    def waves(self) -> list[list[str]]:
        """A mesma ideia do Compose (Capítulo 17): ondas de tarefas independentes, que podem rodar juntas."""
        level: dict[str, int] = {}

        def depth(name, trail=()):
            if name in trail:
                raise ValueError("ciclo: " + " -> ".join([*trail, name]))
            if name not in level:
                deps = self.tasks[name].deps
                level[name] = 0 if not deps else 1 + max(depth(d, (*trail, name)) for d in deps)
            return level[name]

        for name in self.tasks:
            depth(name)
        return [sorted(n for n, l in level.items() if l == i) for i in range(max(level.values()) + 1)]

    def fingerprint(self, name: str, dep_hashes: list[str]) -> str:
        """O que muda o resultado: o CÓDIGO da tarefa e as ENTRADAS (os resultados das dependências)."""
        task = self.tasks[name]
        digest = hashlib.sha256()
        digest.update(inspect.getsource(task.fn).encode())
        for h in dep_hashes:
            digest.update(h.encode())
        return digest.hexdigest()[:16]

    def run(self) -> dict:
        outputs: dict[str, object] = {}
        hashes: dict[str, str] = {}
        failed: set[str] = set()
        for wave in self.waves():
            with ThreadPoolExecutor(self.workers) as pool:
                futures = {name: pool.submit(self._run_one, name, outputs, hashes, failed) for name in wave}
                for name, future in futures.items():
                    status, value, key = future.result()
                    if status == "ok" or status == "cached":
                        outputs[name], hashes[name] = value, key
                    else:
                        failed.add(name)
        return {"outputs": outputs, "failed": sorted(failed)}

    def _record(self, name, status, seconds):
        with self._lock:
            self.log.append((name, status, seconds))

    def _run_one(self, name, outputs, hashes, failed):
        task = self.tasks[name]
        if any(d in failed for d in task.deps):
            self._record(name, "pulada (dependência falhou)", 0.0)
            return "skipped", None, None
        key = self.fingerprint(name, [hashes[d] for d in task.deps])
        cache_file = self.cache_dir / f"{name}-{key}.json"
        if cache_file.exists():
            self._record(name, "em cache", 0.0)
            return "cached", json.loads(cache_file.read_text()), key
        start = time.perf_counter()
        for attempt in range(task.retries + 1):
            try:
                value = task.fn(*[outputs[d] for d in task.deps])
                break
            except Exception as error:
                if attempt == task.retries:
                    self._record(name, f"FALHOU: {error}", time.perf_counter() - start)
                    return "failed", None, None
        tmp = cache_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(value))
        tmp.replace(cache_file)
        self._record(name, "executada" + (f" ({attempt + 1} tentativas)" if attempt else ""), time.perf_counter() - start)
        return "ok", value, key


# ---------- as tarefas do exemplo ----------
state = {"b_calls": 0, "report_broken": True}


def extract_a():
    time.sleep(0.3)
    return [1, 2, 3, 4]


def extract_b():
    state["b_calls"] += 1
    time.sleep(0.3)
    if state["b_calls"] == 1:
        raise ConnectionError("API fora do ar")             # falha só na primeira vez (para testar a nova tentativa)
    return [10, 20, 30]


def clean_a(rows):
    time.sleep(0.2)
    return [r * 2 for r in rows]


def clean_b(rows):
    time.sleep(0.2)
    return [r + 1 for r in rows]


def join(a, b):
    time.sleep(0.2)
    return sum(a) + sum(b)


def report(total):
    if state["report_broken"]:
        raise ValueError("bug no relatório")
    return f"total = {total}"


def build(cache_dir: Path) -> Pipeline:
    return Pipeline([
        Task("extract_a", extract_a), Task("extract_b", extract_b, retries=1),
        Task("clean_a", clean_a, ["extract_a"]), Task("clean_b", clean_b, ["extract_b"]),
        Task("join", join, ["clean_a", "clean_b"]), Task("report", report, ["join"]),
    ], cache_dir)


def show(title, pipeline, result, elapsed):
    print(f"\n{title}: {elapsed:.2f} s | falhas: {result['failed'] or 'nenhuma'}")
    wave_of = {name: i for i, wave in enumerate(pipeline.waves()) for name in wave}
    for name, status, seconds in sorted(pipeline.log, key=lambda entry: (wave_of[entry[0]], entry[0])):
        print(f"  {name:<10} {status:<34} {seconds:5.2f} s")


cache = Path(tempfile.mkdtemp(prefix="dag-"))
print("ondas (o que pode rodar em paralelo):", build(cache).waves())

# 1. primeira execução: paralelismo, uma nova tentativa e um bug no relatório (a tarefa final)
p = build(cache)
start = time.perf_counter()
result = p.run()
show("1ª execução", p, result, time.perf_counter() - start)
print(f"  tempo em série seria ~{0.3 + 0.3 + 0.3 + 0.2 + 0.2 + 0.2 + 0.2:.1f} s; as ondas paralelas fizeram em ~{time.perf_counter() - start:.1f} s")

# 2. corrige o bug e roda de novo: SÓ o que falhou (e depende do que mudou) é refeito; o resto vem do cache
state["report_broken"] = False
p = build(cache)
start = time.perf_counter()
result = p.run()
show("2ª execução (bug corrigido): recomeça de onde parou", p, result, time.perf_counter() - start)
print("  resultado:", result["outputs"]["report"])

# 3. nada mudou: tudo em cache
p = build(cache)
start = time.perf_counter()
result = p.run()
show("3ª execução (nada mudou)", p, result, time.perf_counter() - start)

# 4. mudou a entrada de A: só A e o que depende dele são recalculados (B continua em cache)
def extract_a():
    time.sleep(0.3)
    return [1, 2, 3, 4, 5]                                   # um registro novo na origem


p = build(cache)
p.tasks["extract_a"] = Task("extract_a", extract_a)
start = time.perf_counter()
result = p.run()
show("4ª execução (a origem de A mudou)", p, result, time.perf_counter() - start)
print("  resultado:", result["outputs"]["report"], "| extract_b e clean_b vieram do cache")

# 5. falha em uma ramificação: as dependentes são puladas, as independentes continuam
p = build(Path(tempfile.mkdtemp(prefix="dag-")))
p.tasks["clean_a"] = Task("clean_a", lambda rows: 1 / 0, ["extract_a"])
result = p.run()
show("5ª execução (clean_a quebrou, cache novo)", p, result, 0)
