from huey import RedisHuey

import common

huey = RedisHuey("lab", url=common.REDIS_URL)


@huey.task()
def io_task(task_id, ms=50):
    return common.io_task(task_id, ms)


@huey.task()
def cpu_task(n=25):
    return common.cpu_task(n)


@huey.task(retries=5, retry_delay=0)
def flaky_task(task_id):
    return common.flaky_task(task_id)
