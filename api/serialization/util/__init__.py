from typing import Dict, Any, Callable
import inspect
from functools import wraps
from api.models.openminds.base import BaseModel

class ClsUnregForSerialisationException(Exception): pass

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

def instance_to_model(instance,*, skip_classes=(), **kwargs):
    for Cls in instance.__class__.__mro__:
        if Cls in REGISTER:
            if Cls in skip_classes:
                continue
            return REGISTER[Cls](instance, **kwargs)
    raise ClsUnregForSerialisationException(f"class {instance.__class__}  has not been registered to be serialized!")
    