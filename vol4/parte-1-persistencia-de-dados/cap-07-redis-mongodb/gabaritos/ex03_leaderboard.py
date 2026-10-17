"""Gabarito do exercício 3."""


class Leaderboard:
    def __init__(self, redis, name):
        self.redis, self.key = redis, f"lb:{name}"

    def add(self, member, points):
        return float(self.redis.zincrby(self.key, points, member))

    def score(self, member):
        value = self.redis.zscore(self.key, member)
        return None if value is None else float(value)

    def rank(self, member):
        position = self.redis.zrevrank(self.key, member)
        return None if position is None else position + 1

    def top(self, n):
        if n < 1:
            raise ValueError("n >= 1")
        return [(m, float(s)) for m, s in self.redis.zrevrange(self.key, 0, n - 1, withscores=True)]

    def around(self, member, k):
        position = self.redis.zrevrank(self.key, member)
        if position is None:
            raise KeyError(member)
        low = max(0, position - k)
        rows = self.redis.zrevrange(self.key, low, position + k, withscores=True)
        return [(low + i + 1, m, float(s)) for i, (m, s) in enumerate(rows)]

    def remove(self, member):
        return bool(self.redis.zrem(self.key, member))

    def size(self):
        return self.redis.zcard(self.key)
