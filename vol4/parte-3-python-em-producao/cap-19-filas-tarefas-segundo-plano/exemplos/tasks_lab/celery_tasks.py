import os

from celery import Celery

import common

app = Celery("lab", broker=common.REDIS_URL, backend=common.REDIS_URL.replace("/0", "/1"))
app.conf.task_ignore_result = True
app.conf.broker_connection_retry_on_startup = True
if os.environ.get("TUNED"):                                 # configuração para NÃO perder tarefas quando o worker cai
    app.conf.task_acks_late = True                           # confirma DEPOIS de executar (padrão: antes)
    app.conf.worker_prefetch_multiplier = 1                  # não reserva um monte de mensagens à frente
    app.conf.broker_transport_options = {"visibility_timeout": 10}    # reentrega o que ficou sem confirmação depois de 10 s (padrão: 1 hora)


@app.task(name="io_task")
def io_task(task_id, ms=50):
    return common.io_task(task_id, ms)


@app.task(name="cpu_task")
def cpu_task(n=25):
    return common.cpu_task(n)


@app.task(name="flaky_task", autoretry_for=(ConnectionError,), default_retry_delay=0, max_retries=5)
def flaky_task(task_id):
    return common.flaky_task(task_id)
