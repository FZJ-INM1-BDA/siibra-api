from api.siibra_api_config import ROLE
from api.siibra_api_config import CELERY_CHANNEL, CELERY_CONFIG, QUEUE_PREFIX
from api.common.logger import logger

app = None
if ROLE == "worker" or ROLE == "server":
    from celery import Celery
    logger.info(f"{QUEUE_PREFIX=}, {ROLE=}")
    app = Celery(CELERY_CHANNEL)
    app.config_from_object(CELERY_CONFIG)
else:
    raise RuntimeError(f"worker.app should not be initialized, as ROLE is not set as worker, but as: '{ROLE}'")
