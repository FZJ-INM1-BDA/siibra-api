from api.siibra_api_config import ROLE
from api.siibra_api_config import CELERY_CHANNEL, CELERY_CONFIG

# NB: Celery runs with the solo pool (no fork), so opentelemetry-instrument's
# TracerProvider/BatchSpanProcessor live in the same process that executes
# tasks and export spans directly. CeleryInstrumentor is applied automatically
# by `opentelemetry-instrument`; no manual post-fork re-instrumentation needed.

app = None
if ROLE == "worker" or ROLE == "server":
    from celery import Celery

    app = Celery(CELERY_CHANNEL)
    app.config_from_object(CELERY_CONFIG)
else:
    raise RuntimeError(f"worker.app should not be initialized, as ROLE is not set as worker, but as: '{ROLE}'")
