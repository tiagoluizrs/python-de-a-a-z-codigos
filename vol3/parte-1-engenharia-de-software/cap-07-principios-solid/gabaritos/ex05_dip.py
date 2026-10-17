"""Gabarito do exercício 5."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Reminder:
    id: int
    due: datetime
    to: str
    text: str


class ReminderService:
    def __init__(self, store, send, now, max_attempts=3):
        self.store, self.send, self.now, self.max_attempts = store, send, now, max_attempts

    def run(self):
        current = self.now()
        result = {"sent": [], "failed": [], "waiting": []}
        for reminder in self.store.pending():
            if reminder.due > current:
                result["waiting"].append(reminder.id)
                continue
            for attempt in range(1, self.max_attempts + 1):
                try:
                    self.send(reminder.to, reminder.text)
                except ConnectionError:
                    if attempt == self.max_attempts:
                        result["failed"].append(reminder.id)
                    continue
                self.store.mark_sent(reminder.id)
                result["sent"].append(reminder.id)
                break
        return result


def build_service(env, store, smtp_send=None, clock=None):
    now = clock if clock is not None else datetime.now
    max_attempts = int(env.get("MAX_ATTEMPTS", "3"))
    if "SMTP_HOST" in env:
        if smtp_send is None:
            raise ValueError("smtp_send ausente")
        host = env["SMTP_HOST"]
        return ReminderService(store, lambda to, text: smtp_send(host, to, text), now, max_attempts)
    outbox: list = []
    service = ReminderService(store, lambda to, text: outbox.append((to, text)), now, max_attempts)
    service.outbox = outbox
    return service
