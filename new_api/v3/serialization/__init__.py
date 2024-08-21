from typing import Dict, Type, Callable, Any
from new_api.v3.models._commons import ConfigBaseModel
from new_api.common.exceptions import NonStrKeyException

REGISTER: Dict[Type, Callable[..., ConfigBaseModel]] = {}

def instance_to_model(instance: Any, **kwargs):
    from . import _common
    
    if instance is None:
        return None

    if isinstance(instance, (str, int, float)):
        return instance

    if isinstance(instance, (list, tuple)):
        return [instance_to_model(item, **kwargs) for item in instance]

    if isinstance(instance, dict):
        if not all([isinstance(key, str) for key in instance]):
            raise NonStrKeyException(f"Attempting to serialize dict with non str keys! {instance}")
        return {
            key: instance_to_model(value, **kwargs)
            for key, value in instance.items()
        }

    assert type(instance) in REGISTER, f"{type(instance).__name__} has not been registered."
    return REGISTER[type(instance)](instance, **kwargs)


def serialize(Cls: Type):
    def outer(fn: Callable):
        REGISTER[Cls] = fn
        return fn
    return outer