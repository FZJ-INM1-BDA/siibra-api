from typing import Dict, Callable, Type
import inspect
from functools import wraps
from api.models._commons import ConfigBaseModel

class ClsUnregForSerialisationException(Exception): pass

REGISTER: Dict[Type, Callable[..., ConfigBaseModel]] = {}

def instance_to_model(instance,*, use_class: Type=None, skip_classes=[], **kwargs):
    
    if use_class:
        if use_class not in REGISTER:
            raise IndexError(f"class {str(use_class)} not in register")
        return REGISTER[use_class](instance, **kwargs)
    
    if instance is None:
        return None
    if isinstance(instance, (str, int, float)):
        return instance
    if isinstance(instance, (list, tuple)):
        return [instance_to_model(item) for item in instance]
    if isinstance(instance, dict):
        if not all([isinstance(key, str) for key in instance]):
            raise RuntimeError(f"Attempting to serialize dict with non str keys! {instance}")
        return {
            key: instance_to_model(value)
            for key, value in instance.items()
        }
    for Cls in instance.__class__.__mro__:
        if Cls in REGISTER:
            if Cls in skip_classes or any(issubclass(Cls, SkipCls) for SkipCls in skip_classes):
                continue
            return REGISTER[Cls](instance, **kwargs)
    raise ClsUnregForSerialisationException(f"class {instance.__class__}  has not been registered to be serialized!")


def serialize(Cls, pass_super_model=False, **kwargs):
    assert inspect.isclass(Cls)
    def outer(func: Callable):
        # TODO need to arrange the iteration from most specific to most generic
        def _func(*args, **kwargs):
            super_model = instance_to_model(*args, **kwargs, skip_classes=(Cls,))
            
            super_model_dict = super_model.dict()
            super_model_dict.pop("@type", None)
            return func(*args, **kwargs, super_model_dict=super_model_dict)
            
        real_func = _func if pass_super_model else func

        REGISTER[Cls] = real_func

        @wraps(func)
        def inner(*args, **kwargs):
            return real_func(*args, **kwargs)
        return inner
    return outer
