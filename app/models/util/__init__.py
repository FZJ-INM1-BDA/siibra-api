from typing import Dict, Any, Callable
import inspect
from functools import wraps
from app.models.openminds.base import BaseModel

REGISTER: Dict[Any, Callable[..., BaseModel]] = {}

def serialize(Cls):
    assert inspect.isclass(Cls)
    def outer(func: Callable):
        # TODO need to arrange the iteration from most specific to most generic
        REGISTER[Cls] = func
        @wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        return inner
    return outer
