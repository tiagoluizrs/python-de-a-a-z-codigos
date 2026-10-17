"""Gabarito do exercício 1."""

_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then redis.call('PEXPIRE', KEYS[1], ARGV[1]) end
local ttl = redis.call('PTTL', KEYS[1])
return {count, ttl}
"""


class FixedWindowLimiter:
    def __init__(self, redis, limit, window_ms, prefix="rl"):
        if limit < 1 or window_ms < 1:
            raise ValueError("limit e window_ms >= 1")
        self.redis, self.limit, self.window_ms, self.prefix = redis, limit, window_ms, prefix
        self._script = redis.register_script(_SCRIPT)

    def allow(self, key):
        count, ttl = self._script(keys=[f"{self.prefix}:{key}"], args=[self.window_ms])
        allowed = count <= self.limit
        return allowed, max(0, self.limit - count), 0 if allowed else max(int(ttl), 0)
