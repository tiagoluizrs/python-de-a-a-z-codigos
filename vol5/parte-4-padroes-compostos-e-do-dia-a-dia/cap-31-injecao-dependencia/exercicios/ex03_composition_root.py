"""Exercício 3: a RAIZ DE COMPOSIÇÃO: um único lugar escolhe os concretos; o resto do programa só recebe."""
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


# ---- (Pronto, NÃO edite.) As peças ----
@dataclass(frozen=True)
class Settings:
    env: str = "dev"                                            # "dev", "test" ou "prod"
    dry_run: bool = False                                       # com True, nada é enviado
    store_path: str | None = None                               # onde guardar (None: só em memória)


class SystemClock:
    def __call__(self):
        return datetime.now()


class FixedClock:
    def __init__(self, when):
        self.when = when

    def __call__(self):
        return self.when


class NullMailer:
    def send(self, to, subject):
        pass


class ConsoleMailer:
    def __init__(self):
        self.lines = []

    def send(self, to, subject):
        self.lines.append(f"para {to}: {subject}")


class SmtpMailer:
    def send(self, to, subject):
        raise ConnectionError("sem rede")


class MemoryStore:
    def __init__(self):
        self.records = []

    def add(self, record):
        self.records.append(record)


class JsonFileStore:
    def __init__(self, path):
        self.path = Path(path)

    def add(self, record):
        records = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else []
        records.append(record)
        self.path.write_text(json.dumps(records), encoding="utf-8")


class ReportService:
    def __init__(self, store, mailer, clock):
        self.store, self.mailer, self.clock = store, mailer, clock

    def run(self, name):
        record = {"name": name, "at": self.clock().isoformat()}
        self.store.add(record)
        self.mailer.send("equipe@x.com", f"relatório {name}")
        return record


@dataclass
class App:
    settings: Settings
    report: ReportService
    store: object
    mailer: object
    clock: object


# ---- Implemente a raiz de composição ----
def build_app(settings: Settings, **overrides) -> App:
    """Monta o ``App`` escolhendo os concretos pelas ``settings``. Este é o ÚNICO lugar que decide isso (``ReportService`` e as peças não perguntam o ambiente).

    * ``settings.env`` fora de ``"dev"``, ``"test"`` e ``"prod"``: ``ValueError(f"ambiente desconhecido: {env!r}")``;
    * relógio: ``FixedClock(datetime(2026, 1, 1, 12, 0))`` em ``"test"``; senão ``SystemClock()``;
    * e-mail: ``dry_run`` verdadeiro: ``NullMailer()`` (em QUALQUER ambiente); senão ``"prod"``: ``SmtpMailer()``; senão (``dev``/``test``): ``ConsoleMailer()``;
    * armazenamento: ``store_path`` dado: ``JsonFileStore(store_path)``; senão ``MemoryStore()``; ``"prod"`` SEM ``store_path``: ``ValueError("prod exige store_path")``
      (a validação vem DEPOIS da conferência do ambiente);
    * ``overrides``: argumentos nomeados ``clock=``, ``mailer=`` e ``store=`` SUBSTITUEM o componente escolhido (para os testes); qualquer outro nome: ``TypeError(f"override desconhecido: {nome}")``
      (conferido ANTES de montar qualquer coisa); um override vale mesmo que seja ``None``-like (use ``name in overrides``, não a veracidade);
    * ``report = ReportService(store, mailer, clock)`` com os componentes FINAIS; devolve ``App(settings, report, store, mailer, clock)``;
    * cada chamada cria objetos NOVOS (nenhum estado global, nenhum singleton escondido): dois ``build_app`` não compartilham o armazenamento em memória."""
    raise NotImplementedError
