from fastapi import HTTPException
from fastapi.responses import PlainTextResponse
from api.siibra_api_config import ROLE, CELERY_CONFIG, NAME_SPACE
from functools import wraps
import time


def cached(ttl=60):
    last_call_time = 0
    cached_val = None
    def outer(fn):
        @wraps(fn)
        def inner(*args, **kwargs):

            nonlocal last_call_time
            nonlocal cached_val

            current_time = time.time()
            
            call_original_fn_flag = (cached_val is None) or (current_time - last_call_time > ttl)
            if call_original_fn_flag:
                cached_val = None
                cached_val = fn(*args, **kwargs)
                last_call_time = current_time
            return cached_val
        return inner
    return outer

@cached()
def get_prom_metrics():
    if ROLE != "server":
        raise HTTPException(404, "siibra-api is not configured to be server, so metrics page is not enabled")

    from api.worker.app import app
    from prometheus_client import Gauge, CollectorRegistry, generate_latest
    from prometheus_client.metrics_core import METRIC_NAME_RE

    if not METRIC_NAME_RE.match(NAME_SPACE):
        raise HTTPException(500, detail=f"NAME_SPACE: {NAME_SPACE!r} is not a valid namespace. Please use [a-zA-Z0-9_]+ only!")

    registry = CollectorRegistry()
    common_kwargs = {
        'registry':registry,
        'namespace':NAME_SPACE,
    }
    num_task_in_q_gauge = Gauge(f"num_task_in_q",
                                "Number of tasks in queue (not yet picked up by workers)",
                                labelnames=("q_name",),
                                **common_kwargs)
    num_worker_gauge = Gauge("num_workers", "Number of workers", **common_kwargs)
    scheduled_gauge = Gauge("scheduled_tasks","Number of scheduled tasks",  labelnames=("hostname",), **common_kwargs)
    active_gauge = Gauge("active_tasks", "Number of active tasks", labelnames=("hostname",), **common_kwargs)
    reserved_gauge = Gauge("reserved_tasks", "Number of reserved tasks", labelnames=("hostname",), **common_kwargs)
    

    # assuming we are using redis as broker
    import redis

    _r = redis.from_url(CELERY_CONFIG.broker_url)

    # number of tasks in queue
    for q in CELERY_CONFIG.task_queues.keys():
        num_task_in_q_gauge.labels(q_name=q).set(_r.llen(q))

    i = app.control.inspect()

    # number of active workers
    result = i.ping()
    if result is None:
        num_worker_gauge.set(0)
    else:
        num_worker_gauge.set(len(result))

    for workername, queue in (i.scheduled() or {}).items():
        scheduled_gauge.labels(hostname=workername).set(len(queue))
        
    for workername, queue in (i.active() or {}).items():
        active_gauge.labels(hostname=workername).set(len(queue))
        
    for workername, queue in (i.reserved() or {}).items():
        reserved_gauge.labels(hostname=workername).set(len(queue))

    return PlainTextResponse(generate_latest(registry), status_code=200)
