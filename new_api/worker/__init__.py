from new_api.siibra_api_config import ROLE, CELERY_CHANNEL, CELERY_CONFIG

OTEL_INSTALLED = False
try:
    from opentelemetry.instrumentation.celery import CeleryInstrumentor
    OTEL_INSTALLED = True
except ImportError:
    print("otel not installed. will not try to instrument")

app = None
if ROLE == "worker" or ROLE == "server":
    from celery import Celery

    if OTEL_INSTALLED:
        from celery.signals import worker_process_init
        @worker_process_init.connect(weak=False)
        def init_otel(*args, **kwargs):
            CeleryInstrumentor().instrument()

    app = Celery(CELERY_CHANNEL)
    app.config_from_object(CELERY_CONFIG)
else:
    raise RuntimeError(f"worker.app should not be initialized, as ROLE is not set as worker, but as: '{ROLE}'")
