"""Gabarito do exercício 3."""
import logging
import re


class RedactFilter(logging.Filter):
    def __init__(self, keys=("password", "token", "secret")):
        super().__init__()
        names = "|".join(re.escape(k) for k in keys)
        self._pattern = re.compile(rf'(?<![\w])({names})\s*[=:]\s*("[^"]*"|\'[^\']*\'|\S+)', re.IGNORECASE)

    def filter(self, record):
        message = record.getMessage()
        record.msg = self._pattern.sub(lambda m: f"{m.group(1)}=***", message)
        record.args = ()
        return True


class LevelRangeFilter(logging.Filter):
    def __init__(self, minimum=logging.NOTSET, maximum=None):
        super().__init__()
        self.minimum = minimum
        self.maximum = maximum

    def filter(self, record):
        if record.levelno < self.minimum:
            return False
        return self.maximum is None or record.levelno <= self.maximum
