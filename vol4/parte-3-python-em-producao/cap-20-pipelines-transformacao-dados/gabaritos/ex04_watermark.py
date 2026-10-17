"""Gabarito do exercício 4."""
from datetime import datetime, timedelta

FORMAT = "%Y-%m-%dT%H:%M"
EPOCH = "1970-01-01T00:00"


def shift_minutes(iso, minutes):
    return (datetime.strptime(iso, FORMAT) + timedelta(minutes=minutes)).strftime(FORMAT)


class IncrementalExtractor:
    def __init__(self, state, fetch, overlap_minutes=0, key="id", cursor="updated_at"):
        self.state, self.fetch, self.overlap, self.key, self.cursor = state, fetch, overlap_minutes, key, cursor

    def run(self):
        watermark = self.state.get("watermark", EPOCH)
        seen = set(self.state.get("seen", set()))
        rows = self.fetch(shift_minutes(watermark, -self.overlap) if self.overlap else watermark)
        new = [r for r in rows if (r[self.key], r[self.cursor]) not in seen]
        new.sort(key=lambda r: (r[self.cursor], r[self.key]))
        newest = max([watermark] + [r[self.cursor] for r in rows])
        keep_from = shift_minutes(newest, -self.overlap) if self.overlap else newest
        seen |= {(r[self.key], r[self.cursor]) for r in rows}
        seen = {pair for pair in seen if pair[1] >= keep_from}
        self.state["watermark"], self.state["seen"] = newest, seen
        return {"new": new, "watermark": newest, "fetched": len(rows)}
