from typing import Literal, Union
from functools import wraps

from .logger import logger
from .exceptions import FaultyRoleException

def dummy(*args, **kwargs): pass

ROLE_TYPE = Union[Literal['worker'], Literal["server"], Literal["all"]]

def data_decorator(role: ROLE_TYPE):
    """data decorator

    Extensively used in new_api.v3.common.data_handlers. Most of the business logic, including data fetching, serialization, etc.
    
    Args:
        role: Role of this process
    
    Raises:
        ImportError: Celery not installed, but role is set to either `worker` or `server`
    """
    if role != "worker":
        logger.warning(f"Role was set to be {role}, calls to map/* endpoints will fail. See https://github.com/FZJ-INM1-BDA/siibra-api/issues/151")
    def outer_wrapper(fn):
        if role == "all":
            return fn
        if role == "worker" or role == "server":
            try:
                from ..worker import app
                
                def celery_task_wrapper(self, *args, **kwargs):
                    return fn(*args, **kwargs)
                    
                return app.task(bind=True)(
                    wraps(fn)(celery_task_wrapper)
                )
            except ImportError as e:
                errmsg = f"For worker role, celery must be installed as a dep"
                logger.critical(errmsg)
                raise ImportError(errmsg) from e
        raise FaultyRoleException(f"role must be 'all', 'server' or 'worker', but it is {role}")
    return outer_wrapper