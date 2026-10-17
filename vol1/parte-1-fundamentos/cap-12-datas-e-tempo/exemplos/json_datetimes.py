"""datetime não é serializável em JSON: converta para ISO 8601."""
import datetime as dt
import json

event = {"name": "deploy",
         "at": dt.datetime(2026, 10, 12, 17, 30, tzinfo=dt.UTC)}
try:
    json.dumps(event)
except TypeError as error:
    print("TypeError:", error)


def default(value):
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    raise TypeError(f"não serializável: {type(value).__name__}")


text = json.dumps(event, default=default)
print(text)
back = json.loads(text)
back["at"] = dt.datetime.fromisoformat(back["at"])   # volta explícita
print(back, back["at"] == event["at"])
