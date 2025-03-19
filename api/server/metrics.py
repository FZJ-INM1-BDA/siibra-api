from fastapi import HTTPException
from fastapi.responses import PlainTextResponse
from typing import Dict, Tuple, Callable
from subprocess import run
import os
from pathlib import Path
from collections import defaultdict
from functools import wraps
from api.siibra_api_config import ROLE, CELERY_CONFIG, NAME_SPACE, MONITOR_FIRSTLVL_DIR
from api.common.timer import Cron
from api.common import general_logger

def is_server(fn: Callable):
    @wraps(fn)
    def outer():
        if ROLE != 'server':
            return
        return fn()
    return outer

def has_metric_dir(fn: Callable):
    @wraps(fn)
    def outer():
        if not MONITOR_FIRSTLVL_DIR:
            return
        return fn()
    return outer

cron = Cron()

class Singleton:
    """Timer singleton"""
    cached_metrics=None
    cached_du: Dict[str, str] = {}
    res_mtime: float = None
    cached_res_usage: Dict[str, Tuple[float, float]] = {}

    @staticmethod
    @cron.minutely
    @has_metric_dir
    @is_server
    def parse_metrics_txt():
        def parse_cpu(text: str) -> float:
            if text.endswith("m"):
                return float(text.replace("m", ""))
            raise ValueError(f"Cannot parse cpu text {text}")
        
        def parse_memory(text: str) -> float:
            if text.endswith("Mi"):
                return float(text.replace("Mi", "")) * 1024 * 1024
            raise ValueError(f"Cannot parse memory text {text}")
        
        def parse_text(text: str):
            titles = ["NAME", "CPU", "MEMORY"]
            
            Singleton.cached_res_usage.clear()

            for line in text.splitlines():
                if all(t in line for t in titles):
                    continue
                podname, cpuusage, memoryusage = line.split()
                try:
                    Singleton.cached_res_usage[podname] = (
                        str(parse_cpu(cpuusage)),
                        str(parse_memory(memoryusage)),
                    )
                except Exception as e:
                    general_logger.error(f"Cannot parse line: {str(e)}")

        try:
            metrics_path = Path(MONITOR_FIRSTLVL_DIR) / "metrics.txt"
            metric_text = metrics_path.read_text()
            Singleton.res_mtime = metrics_path.lstat().st_mtime
            parse_text(metric_text)
            
        except FileNotFoundError as e:
            ...
        except Exception as e:
            general_logger.error(f"Reading metrics.txt error: {str(e)}")

    @staticmethod
    @cron.ten_minutely
    @has_metric_dir
    @is_server
    def first_lvl_du():

        try:
            dirs = os.listdir(MONITOR_FIRSTLVL_DIR)
        except Exception as e:
            general_logger.warning(f"Failed to listdir of {MONITOR_FIRSTLVL_DIR}: {str(e)}")
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
                general_logger.warning(f"Failed to check du of {str(path_to_dir)}: {str(e)}")

    @staticmethod
    @cron.minutely
    @is_server
    def refresh_metric():
        """Refresh metrics."""
        from api.worker.app import app
        from prometheus_client import Gauge, CollectorRegistry, generate_latest

        registry = CollectorRegistry()
        common_kwargs = {
            'registry':registry,
        }

        cpu_usage = Gauge("resource_usage_cpu",
                        "CPU usage by pods",
                        labelnames=("podname",),
                        **common_kwargs)
        
        memory_usage = Gauge("resource_usage_memory",
                        "RAM usage by pods",
                        labelnames=("podname",),
                        **common_kwargs)
        
        for podname, (cpu, ram) in Singleton.cached_res_usage.items():
            cpu_usage.labels(podname=podname).set(cpu)
            memory_usage.labels(podname=podname).set(ram)
        
        res_timestamp = Gauge("resource_usage_timestamp",
                            "Timestamp", **common_kwargs)
        if Singleton.res_mtime:
            res_timestamp.set(Singleton.res_mtime)

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
        
        tally = defaultdict(int)
        for hostname in (result or {}):
            for queue in result[hostname]:
                routing_key = queue.get("routing_key")
                try:
                    *_, namespace, queue = routing_key.split(".")
                    version = ".".join(_)
                    tally[(version, namespace, queue)] += 1
                except:
                    tally[(routing_key, None, None)] += 1

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

        Singleton.cached_metrics = generate_latest(registry)


@is_server
def on_startup():
    """On startup"""

    # Set cached_metrics first
    # Populating metrics takes a while

    from prometheus_client import Gauge, CollectorRegistry, generate_latest
    registry = CollectorRegistry()
    common_kwargs = {
        'registry':registry,
        'namespace':NAME_SPACE,
    }
    last_pinged = Gauge("last_pinged", "Last pinged time", labelnames=[], **common_kwargs)
    last_pinged.set_to_current_time()
    Singleton.cached_metrics = generate_latest(registry)

    cron.start()


@is_server
def on_terminate():
    """On terminate"""
    cron.stop()


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
