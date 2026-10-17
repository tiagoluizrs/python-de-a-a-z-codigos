"""Gabarito do exercício 4."""


class ReliableQueue:
    def __init__(self, redis, name):
        self.redis, self.queue = redis, f"q:{name}"

    def _processing(self, worker):
        return f"{self.queue}:processing:{worker}"

    def put(self, item):
        return self.redis.rpush(self.queue, item)

    def get(self, worker, timeout=1):
        return self.redis.blmove(self.queue, self._processing(worker), timeout, "LEFT", "RIGHT")

    def ack(self, worker, item):
        return self.redis.lrem(self._processing(worker), 1, item) == 1

    def recover(self, worker):
        count = 0
        while self.redis.lmove(self._processing(worker), self.queue, "RIGHT", "LEFT") is not None:
            count += 1
        return count

    def pending(self, worker):
        return self.redis.lrange(self._processing(worker), 0, -1)

    def size(self):
        return self.redis.llen(self.queue)
