"""Gabarito do exercício 6."""
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout


class HealthChecker:
    def __init__(self):
        self._checks: dict = {}

    def add(self, name, fn, critical=True, timeout=0.5):
        if name in self._checks:
            raise ValueError(f"verificação repetida: {name}")
        self._checks[name] = (fn, critical, timeout)

    def run(self):
        if not self._checks:
            return 200, {"status": "ok", "checks": {}}
        pool = ThreadPoolExecutor(len(self._checks))
        start = time.perf_counter()
        futures = {}
        for name, (fn, _, _) in self._checks.items():
            def timed(fn=fn):
                began = time.perf_counter()
                try:
                    fn()
                    return {"status": "ok", "ms": int((time.perf_counter() - began) * 1000)}
                except Exception as error:
                    return {"status": "fail", "error": str(error), "ms": int((time.perf_counter() - began) * 1000)}
            futures[name] = pool.submit(timed)
        checks, down, degraded = {}, False, False
        for name, (_, critical, timeout) in self._checks.items():
            remaining = max(timeout - (time.perf_counter() - start), 0.001)
            try:
                result = futures[name].result(timeout=remaining)
            except FutureTimeout:
                result = {"status": "timeout", "ms": int(timeout * 1000)}
            checks[name] = result
            if result["status"] != "ok":
                down, degraded = down or critical, degraded or not critical
        pool.shutdown(wait=False, cancel_futures=True)
        status = "down" if down else "degraded" if degraded else "ok"
        return (503 if down else 200), {"status": status, "checks": checks}
