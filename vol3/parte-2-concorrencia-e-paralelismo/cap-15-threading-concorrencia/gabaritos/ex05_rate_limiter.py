"""Gabarito do exercício 5."""
import threading
import time


class RateLimiter:
    def __init__(self, rate, burst, clock=time.monotonic, sleep=time.sleep):
        if rate <= 0 or burst < 1:
            raise ValueError("rate > 0 e burst >= 1")
        self._rate, self._burst, self._clock, self._sleep = rate, burst, clock, sleep
        self._tokens = float(burst)
        self._last = clock()
        self._lock = threading.Lock()

    def _refill(self):
        now = self._clock()
        self._tokens = min(self._burst, self._tokens + (now - self._last) * self._rate)
        self._last = now

    def try_acquire(self, n=1):
        if n > self._burst:
            raise ValueError("n maior que burst")
        with self._lock:
            self._refill()
            if self._tokens >= n:
                self._tokens -= n
                return True
            return False

    def acquire(self, n=1):
        if n > self._burst:
            raise ValueError("n maior que burst")
        waited = 0.0
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= n:
                    self._tokens -= n
                    return waited
                needed = (n - self._tokens) / self._rate
            self._sleep(needed)                    # dorme FORA da trava
            waited += needed
