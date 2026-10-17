"""ISO 8601 com datetime: isoformat e fromisoformat (3.11+)."""
import datetime as dt

moment = dt.datetime(2026, 10, 12, 9, 30, 15, 123456, tzinfo=dt.UTC)
print(moment.isoformat())
print(moment.isoformat(timespec="seconds"))
print(moment.isoformat(timespec="milliseconds"))
print(moment.isoformat(sep=" ", timespec="minutes"))
print(dt.date(2026, 10, 12).isoformat(), dt.time(9, 30).isoformat())
print(moment.isocalendar())

samples = [
    "2026-10-12",
    "20261012",
    "2026-10-12T09:30",
    "20261012T093015",
    "2026-10-12 09:30:15",
    "2026-10-12T09:30:15Z",
    "2026-10-12T09:30:15+0300",
    "2026-10-12T09:30:15+03",
    "2026-10-12T09:30:15.123456789+03:00",
    "2026-10-12T09:30:15,5",
    "2026-W42-1",
    "2026-10-12T09",
    "2026-10-12_09:30",
    "2026-10-12T24:00",
    "2026-10",
    "2026-285",
    "2026-1-12",
    "2026-10-12T09:30:15z",
    " 2026-10-12",
]
for text in samples:
    try:
        parsed = dt.datetime.fromisoformat(text)
        print(f"{text!r:40} -> {parsed.isoformat()}")
    except ValueError as error:
        print(f"{text!r:40} -> ValueError: {error}")
