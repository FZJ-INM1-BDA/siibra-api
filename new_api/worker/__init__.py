from new_api.siibra_api_config import ROLE, CELERY_CHANNEL, CELERY_CONFIG

app = None
if ROLE == "worker" or ROLE == "server":
    from celery import Celery
    app = Celery(CELERY_CHANNEL)
    app.config_from_object(CELERY_CONFIG)
else:
    raise RuntimeError(f"worker.app should not be initialized, as ROLE is not set as worker, but as: '{ROLE}'")
