"""Gabarito do exercício 3."""
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    env: str = "dev"
    dry_run: bool = False
    store_path: str | None = None


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


def build_app(settings, **overrides):
    unknown = set(overrides) - {"clock", "mailer", "store"}
    if unknown:
        raise TypeError(f"override desconhecido: {sorted(unknown)[0]}")
    if settings.env not in ("dev", "test", "prod"):
        raise ValueError(f"ambiente desconhecido: {settings.env!r}")
    if settings.env == "prod" and not settings.store_path:
        raise ValueError("prod exige store_path")
    clock = overrides["clock"] if "clock" in overrides else (FixedClock(datetime(2026, 1, 1, 12, 0)) if settings.env == "test" else SystemClock())
    if "mailer" in overrides:
        mailer = overrides["mailer"]
    elif settings.dry_run:
        mailer = NullMailer()
    elif settings.env == "prod":
        mailer = SmtpMailer()
    else:
        mailer = ConsoleMailer()
    if "store" in overrides:
        store = overrides["store"]
    else:
        store = JsonFileStore(settings.store_path) if settings.store_path else MemoryStore()
    return App(settings, ReportService(store, mailer, clock), store, mailer, clock)
