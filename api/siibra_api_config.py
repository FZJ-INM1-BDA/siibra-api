import os

ROLE = os.environ.get("SIIBRA_API_ROLE", "all")

CELERY_CHANNEL = os.environ.get("SIIBRA_API_CELERY_CHANNEL", "siibra-api")

class CELERY_CONFIG:
    broker_url=os.getenv("SIIBRA_API_CELERY_BROKER", "redis://127.0.0.1:6379")
    result_backend=os.getenv("SIIBRA_API_CELERY_RESULT", "redis://127.0.0.1:6379")

    worker_send_task_events = True
    task_send_sent_event = True

    include=['api.common.data_handlers', 'api.serialization']

LOGGER_DIR = os.environ.get("SIIBRA_API_LOG_DIR")

REDIS_HOST = os.getenv("SIIBRA_REDIS_SERVICE_HOST") or os.getenv("REDIS_SERVICE_HOST") or os.getenv("REDIS_HOST") or "localhost"
REDIS_PORT = os.getenv("SIIBRA_REDIS_SERVICE_PORT") or os.getenv("REDIS_SERVICE_PORT") or os.getenv("REDIS_PORT") or 6379
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

IS_CI = os.getenv("CI") is not None
