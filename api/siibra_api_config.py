import os

__version__ = "0.3.5"

NAME_SPACE = os.environ.get("SIIBRA_API_NAMESPACE", "siibraapi")

ROLE = os.environ.get("SIIBRA_API_ROLE", "all")

CELERY_CHANNEL = os.environ.get("SIIBRA_API_CELERY_CHANNEL", f"siibra-api-{__version__}")

REDIS_HOST = os.getenv("SIIBRA_API_REDIS_HOST") or os.getenv("SIIBRA_REDIS_SERVICE_HOST") or os.getenv("REDIS_SERVICE_HOST") or os.getenv("REDIS_HOST") or "localhost"
REDIS_PORT = os.getenv("SIIBRA_API_REDIS_PORT") or os.getenv("SIIBRA_REDIS_SERVICE_PORT") or os.getenv("REDIS_SERVICE_PORT") or os.getenv("REDIS_PORT") or 6379
REDIS_PASSWORD = os.getenv("SIIBRA_API_REDIS_PASSWORD")

QUEUE_PREFIX = f"{__version__}.{NAME_SPACE}"

_queues = [
    "core",
    "features",
    "volumes",
    "compounds",
]

class CELERY_CONFIG:
    broker_url=os.getenv("SIIBRA_API_CELERY_BROKER", f"redis://{(':' + REDIS_PASSWORD + '@') if REDIS_PASSWORD else ''}{REDIS_HOST}:{REDIS_PORT}")
    result_backend=os.getenv("SIIBRA_API_CELERY_RESULT", f"redis://{(':' + REDIS_PASSWORD + '@') if REDIS_PASSWORD else ''}{REDIS_HOST}:{REDIS_PORT}")
    result_expires=60
    worker_send_task_events = True
    task_send_sent_event = True
    
    # see https://docs.celeryq.dev/en/stable/userguide/optimizing.html#reserve-one-task-at-a-time
    task_acks_late = True
    worker_prefetch_multiplier = 1

    # https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-task_time_limit
    # some long running tasks can take a while, but should not exceed 10 minutes to run
    task_time_limit = 600

    include=['api.common.data_handlers', 'api.serialization']

    # source of truth on all queues
    task_routes={
        f'api.common.data_handlers.{_queue}.*': f'{QUEUE_PREFIX}.{_queue}'
        for _queue in _queues
    }

    # define task_queues explicitly, so that if -Q is not defined, the worker
    # will pick up all tasks
    task_queues = {
        'celery': {}, # default queue
        **{
            route: {}
            for route in task_routes.values()
        }
    }

LOGGER_DIR = os.environ.get("SIIBRA_API_LOG_DIR")

IS_CI = os.getenv("CI") is not None

# Volume shared between worker and server
import tempfile
SIIBRA_API_SHARED_DIR = os.getenv("SIIBRA_API_SHARED_DIR") or os.getenv("SIIBRA_CACHEDIR") or tempfile.gettempdir()

import re

SIIBRA_API_REMAP_PROVIDERS = {}
try:
    remapped_providers = os.getenv("SIIBRA_API_REMAP_PROVIDERS")
    if remapped_providers:
        for mapping in remapped_providers.split("\n"):
            regex_string = r"^(?P<from_host>(https?://)?[\w0-9./]+(:[0-9]+)?):(?P<to_host>(https?://)?[\w0-9./]+(:[0-9]+)?)$"
            match = re.match(regex_string, mapping)
            assert match
            SIIBRA_API_REMAP_PROVIDERS[match.group("from_host")] = match.group("to_host")
        
except Exception as e:
    print(f"""Cannot parse SIIBRA_API_REMAP_PROVIDERS properly.
    SIIBRA_API_REMAP_PROVIDERS must be comma separated values, with colon indicating mapping
    e.g.
    me.local:localhost
    SIIBRA_API_REMAP_PROVIDERS
    {remapped_providers}
    """)

GIT_HASH = os.getenv("GIT_HASH", "unknown-hash")