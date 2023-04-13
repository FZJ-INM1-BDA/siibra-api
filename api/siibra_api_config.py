import os

__version__ = "0.3.0"

NAME_SPACE = os.environ.get("SIIBRA_API_NAMESPACE", "siibra_api")

ROLE = os.environ.get("SIIBRA_API_ROLE", "all")

CELERY_CHANNEL = os.environ.get("SIIBRA_API_CELERY_CHANNEL", f"siibra-api-{__version__}")

REDIS_HOST = os.getenv("SIIBRA_API_REDIS_HOST") or os.getenv("SIIBRA_REDIS_SERVICE_HOST") or os.getenv("REDIS_SERVICE_HOST") or os.getenv("REDIS_HOST") or "localhost"
REDIS_PORT = os.getenv("SIIBRA_API_REDIS_PORT") or os.getenv("SIIBRA_REDIS_SERVICE_PORT") or os.getenv("REDIS_SERVICE_PORT") or os.getenv("REDIS_PORT") or 6379
REDIS_PASSWORD = os.getenv("SIIBRA_API_REDIS_PASSWORD")

class CELERY_CONFIG:
    broker_url=os.getenv("SIIBRA_API_CELERY_BROKER", f"redis://{(':' + REDIS_PASSWORD + '@') if REDIS_PASSWORD else ''}{REDIS_HOST}:{REDIS_PORT}")
    result_backend=os.getenv("SIIBRA_API_CELERY_RESULT", f"redis://{(':' + REDIS_PASSWORD + '@') if REDIS_PASSWORD else ''}{REDIS_HOST}:{REDIS_PORT}")
    result_expires=60
    worker_send_task_events = True
    task_send_sent_event = True

    include=['api.common.data_handlers', 'api.serialization']

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
