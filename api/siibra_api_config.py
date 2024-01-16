"""This module houses the configuration of siibra-api.

This should be the only place where user can influence the configuration of siibra-api.

As siibra-api will attempt to load this module, user can either configure siibra-api with environment variables,
or overwrite the this file directly (with docker volume mount, for example)."""

import os
from pathlib import Path
import re

SIIBRA_USE_CONFIGURATION = os.getenv("SIIBRA_USE_CONFIGURATION")

# Rather than using git rev-parse --short HEAD
# Directly crawl through the git file system
# So siibra-api does not have to rely on target system having git installed
def get_config_dir_short_hash(path_to_config: str):
    head_file = Path(path_to_config) / '.git' / 'HEAD'
    if head_file.is_file():
        with open(head_file, "r") as fp:
            head_content = fp.read()
        
        if re.match(r'^[a-f0-9]+$', head_content):
            return head_content[:6]

        if head_content.startswith("ref: "):
            path_to_ref = Path(path_to_config) / '.git' / head_content.replace("ref: ", "").strip()
            if path_to_ref.is_file():
                with open(path_to_ref, "r") as fp:
                    ref_content = fp.read()
                    if re.match(r'^[a-f0-9]+$', ref_content):
                        return ref_content[:6]

_config_hash = SIIBRA_USE_CONFIGURATION and get_config_dir_short_hash(SIIBRA_USE_CONFIGURATION)

# allowing potentially other hashes to be populated here.
# e.g. siibra-python hash, siibra-api hash
with open(Path(__file__).parent / 'VERSION', 'r') as fp:
    __version__ = fp.read()
__version__ = (_config_hash and f"c.{_config_hash}") or __version__
"""siibra api version"""

NAME_SPACE = os.environ.get("SIIBRA_API_NAMESPACE", "siibraapi")
"""NAME_SPACE"""

ROLE = os.environ.get("SIIBRA_API_ROLE", "all")
"""ROLE"""

CELERY_CHANNEL = os.environ.get("SIIBRA_API_CELERY_CHANNEL", f"siibra-api-{__version__}")
"""CELERY_CHANNEL"""

REDIS_HOST = os.getenv("SIIBRA_API_REDIS_HOST") or os.getenv("SIIBRA_REDIS_SERVICE_HOST") or os.getenv("REDIS_SERVICE_HOST") or os.getenv("REDIS_HOST") or "localhost"
"""REDIS_HOST"""

REDIS_PORT = os.getenv("SIIBRA_API_REDIS_PORT") or os.getenv("SIIBRA_REDIS_SERVICE_PORT") or os.getenv("REDIS_SERVICE_PORT") or os.getenv("REDIS_PORT") or 6379
"""REDIS_PORT"""

REDIS_PASSWORD = os.getenv("SIIBRA_API_REDIS_PASSWORD")
"""REDIS_PASSWORD"""

QUEUE_PREFIX = f"{__version__}.{NAME_SPACE}"
"""QUEUE_PREFIX"""

MONITOR_FIRSTLVL_DIR = os.getenv("MONITOR_FIRSTLVL_DIR")
"""MONITOR_FIRSTLVL_DIR"""

_queues = [
    "core",
    "features",
    "volumes",
    "compounds",
    "vocabularies",
]

class CELERY_CONFIG:
    """CELERY_CONFIG"""
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
"""GIT_HASH"""
