import os

import dramatiq
from dramatiq.brokers.redis import RedisBroker

import common

broker = RedisBroker(url=common.REDIS_URL, **({"heartbeat_timeout": 5000, "maintenance_chance": 1} if os.environ.get("TUNED") else {}))
dramatiq.set_broker(broker)


@dramatiq.actor
def io_task(task_id, ms=50):
    return common.io_task(task_id, ms)


@dramatiq.actor
def cpu_task(n=25):
    return common.cpu_task(n)


@dramatiq.actor(max_retries=5, min_backoff=100, max_backoff=500)
def flaky_task(task_id):
    return common.flaky_task(task_id)
