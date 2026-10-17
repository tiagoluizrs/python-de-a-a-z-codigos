"""Gabarito do exercício 2."""
import json
import logging
from datetime import UTC, datetime

STANDARD = set(vars(logging.LogRecord("", 0, "", 0, "", (), None))) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        moment = datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds")
        data = {
            "time": moment.replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in sorted(vars(record)):
            if key not in STANDARD:
                data[key] = vars(record)[key]
        if record.exc_info:
            data["exc"] = self.formatException(record.exc_info)
        return json.dumps(data, ensure_ascii=False, default=str)
