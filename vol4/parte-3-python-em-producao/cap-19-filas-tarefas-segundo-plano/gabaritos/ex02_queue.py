"""Gabarito do exercício 2."""


class FakeClock:
    def __init__(self, now=0.0):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class ReliableQueue:
    def __init__(self, clock, visibility=30.0, max_attempts=3, retry_delay=lambda attempts: 1.0):
        self.clock, self.visibility, self.max_attempts, self.retry_delay = clock, visibility, max_attempts, retry_delay
        self._messages: dict[str, dict] = {}
        self._order = 0
        self._dead: list[str] = []

    def put(self, payload, delay=0.0):
        self._order += 1
        msg_id = f"m{self._order}"
        self._messages[msg_id] = {"payload": payload, "order": self._order, "available_at": self.clock() + delay,
                                  "deadline": None, "attempts": 0, "state": "queued"}
        return msg_id

    def get(self):
        now = self.clock()
        candidates = [(m["order"], i) for i, m in self._messages.items() if m["state"] == "queued" and m["available_at"] <= now]
        if not candidates:
            return None
        _, msg_id = min(candidates)
        message = self._messages[msg_id]
        message["state"], message["deadline"] = "inflight", now + self.visibility
        return msg_id, message["payload"]

    def _inflight(self, msg_id):
        message = self._messages.get(msg_id)
        if message is None or message["state"] != "inflight":
            raise KeyError(msg_id)
        return message

    def ack(self, msg_id):
        self._inflight(msg_id)
        del self._messages[msg_id]

    def _failed(self, msg_id, message, delay_if_retry):
        message["attempts"] += 1
        if message["attempts"] >= self.max_attempts:
            message["state"] = "dead"
            self._dead.append(msg_id)
            return None
        message["state"], message["deadline"] = "queued", None
        message["available_at"] = self.clock() + delay_if_retry(message["attempts"])
        return self.retry_delay(message["attempts"])

    def nack(self, msg_id):
        message = self._inflight(msg_id)
        return self._failed(msg_id, message, self.retry_delay)

    def reap(self):
        now = self.clock()
        expired = [(i, m) for i, m in self._messages.items() if m["state"] == "inflight" and m["deadline"] <= now]
        for msg_id, message in expired:
            self._failed(msg_id, message, lambda attempts: 0.0)
        return len(expired)

    def attempts(self, msg_id):
        return self._messages[msg_id]["attempts"]

    def sizes(self):
        now = self.clock()
        counts = {"ready": 0, "inflight": 0, "delayed": 0, "dead": len(self._dead)}
        for m in self._messages.values():
            if m["state"] == "inflight":
                counts["inflight"] += 1
            elif m["state"] == "queued":
                counts["ready" if m["available_at"] <= now else "delayed"] += 1
        return counts

    @property
    def dead(self):
        return list(self._dead)
