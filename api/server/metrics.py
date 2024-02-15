from fastapi import HTTPException
from fastapi.responses import PlainTextResponse
from typing import List, Dict
from subprocess import run
import os
from pathlib import Path
from collections import defaultdict
from api.siibra_api_config import ROLE, CELERY_CONFIG, NAME_SPACE, MONITOR_FIRSTLVL_DIR, queues
from api.common.timer import RepeatTimer
from api.common import general_logger

class Singleton:
    """Timer singleton"""
    cached_metrics=None
    cached_du: Dict[str, str] = {}
    timers: List[RepeatTimer] = []

    @staticmethod
    def populate_celery():
        if ROLE == 'server':
            Singleton.cached_metrics = refresh_prom_metrics()

    @staticmethod
    def timed_du():
        if ROLE == 'server' and MONITOR_FIRSTLVL_DIR:
            # n.b. cannot use shutil.disk_usage . It seems it 
            # queries mount used/free and not directory
            try:
                dirs = os.listdir(MONITOR_FIRSTLVL_DIR)
            except Exception as e:
                general_logger.warn(f"Failed to listdir of {MONITOR_FIRSTLVL_DIR}: {str(e)}")
                return
            
            for dir in dirs:
                if dir == "lost+found":
                    continue
                path_to_dir = Path(MONITOR_FIRSTLVL_DIR) / dir
                try:
                    result = run(["du", "-s", str(path_to_dir)], capture_output=True, text=True)
                    size_b, *_ = result.stdout.split("\t")
                    Singleton.cached_du[dir] = int(size_b)
                except Exception as e:
                    general_logger.warn(f"Failed to check du of {str(path_to_dir)}: {str(e)}")
            

def on_startup():
    """On startup"""
    Singleton.populate_celery()
    Singleton.timed_du()

    Singleton.timers = [
        RepeatTimer(60, Singleton.populate_celery),
        RepeatTimer(600, Singleton.timed_du),
    ]

    for timer in Singleton.timers:
        timer.start()

    
def on_terminate():
    """On terminate"""
    for timer in Singleton.timers:
        timer.cancel()

def refresh_prom_metrics():
    """Refresh metrics."""
    from api.worker.app import app
    from prometheus_client import Gauge, CollectorRegistry, generate_latest

    registry = CollectorRegistry()
    common_kwargs = {
        'registry':registry,
        'namespace':NAME_SPACE,
    }

    du = Gauge(f"firstlvl_folder_disk_usage",
               "Bytes used by first level folders",
               labelnames=("folder_name",),
               **common_kwargs)
    for folder_name, size_b in Singleton.cached_du.items():
        du.labels(folder_name=folder_name).set(size_b)

    num_task_in_q_gauge = Gauge(f"num_task_in_q",
                                "Number of tasks in queue (not yet picked up by workers)",
                                labelnames=("q_name",),
                                **common_kwargs)
    num_worker_gauge = Gauge("num_workers",
                             "Number of workers",
                             labelnames=("version", "namespace", "queue"), **common_kwargs)
    scheduled_gauge = Gauge("scheduled_tasks","Number of scheduled tasks",  labelnames=("hostname",), **common_kwargs)
    active_gauge = Gauge("active_tasks", "Number of active tasks", labelnames=("hostname",), **common_kwargs)
    reserved_gauge = Gauge("reserved_tasks", "Number of reserved tasks", labelnames=("hostname",), **common_kwargs)
    last_pinged = Gauge("last_pinged", "Last pinged time", labelnames=[], **common_kwargs)

    # assuming we are using redis as broker
    import redis

    _r = redis.from_url(CELERY_CONFIG.broker_url)

    last_pinged.set_to_current_time()

    # number of tasks in queue
    for q in CELERY_CONFIG.task_queues.keys():
        num_task_in_q_gauge.labels(q_name=q).set(_r.llen(q))

    i = app.control.inspect()

    # number of active workers
    result = app.control.inspect().active_queues()
    
    tally = defaultdict(0)
    for hostname in result:
        for queue in result[hostname]:
            routing_key = queue.get("routing_key")
            *_, namespace, queue = routing_key
            version = ".".join(_)
            tally[(version, namespace, queue)] += 1

    for ((version, namespace, queue), total) in tally.items():
        num_worker_gauge.labels(version=version,
                                namespace=namespace,
                                queue=queue).set(total)

    for workername, queue in (i.scheduled() or {}).items():
        scheduled_gauge.labels(hostname=workername).set(len(queue))
        
    for workername, queue in (i.active() or {}).items():
        active_gauge.labels(hostname=workername).set(len(queue))
        
    for workername, queue in (i.reserved() or {}).items():
        reserved_gauge.labels(hostname=workername).set(len(queue))

    return generate_latest(registry)

def prom_metrics_resp():
    """Return PlainTextResponse of metrics"""
    if ROLE != "server":
        raise HTTPException(404, "siibra-api is not configured to be server, so metrics page is not enabled")
    
    from prometheus_client.metrics_core import METRIC_NAME_RE
    
    if not METRIC_NAME_RE.match(NAME_SPACE):
        raise HTTPException(500, detail=f"NAME_SPACE: {NAME_SPACE!r} is not a valid namespace. Please use [a-zA-Z0-9_]+ only!")

    if Singleton.cached_metrics is None:
        raise HTTPException(404, 'Not yet populated. Please wait ...')
    
    return PlainTextResponse(Singleton.cached_metrics, status_code=200)
