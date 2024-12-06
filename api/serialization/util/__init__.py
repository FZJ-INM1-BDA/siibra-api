from typing import Dict, Callable, Type, List
import inspect
from functools import wraps
from api.models._commons import ConfigBaseModel
from api.common.exceptions import (
    ClsNotRegisteredException,
    NonStrKeyException,
)
from typing import Any, Dict, _GenericAlias
import math

REGISTER: Dict[Type, Callable[..., ConfigBaseModel]] = {}

def sanitize_cls(Cls):
    if isinstance(Cls, _GenericAlias):
        return Cls
    
    assert inspect.isclass(Cls), f"Expecting {str(Cls)} to be a class, but is not."
    return Cls

def is_generic_instance(inst):
    return hasattr(inst, "__orig_class__")

def instance_to_model(instance: Any, * , use_class: Type=None, skip_classes: List[Type]=[], **kwargs: Dict[str, Any]):
    """Serialize instance into model, according to register.

    Args:
        instance: instance to be serialized
        use_class: use registered method for this specific class for serialization
        skip_classes: skip registered method for these classes
        kwargs: keyword arguements to be passed to downstream instance_to_model calls
    
    Return:
        Serialized intances
    
    Raises:
        ClsNotRegisteredException: if `use_class` is provided and use_class is not registered
        ClsNotRegisteredException: if no suitable serialization can be found for `instance.__class__`
        NonStrKeyException: if instance contains a dictionary, which do not have str as keys
    """
    if is_generic_instance(instance):
        if use_class:
            assert use_class == instance.__orig_class__, f"instance {str(instance)} is a instance of generic type. use_class must == instance.__orig_class__"
        use_class = instance.__orig_class__
    if use_class:
        use_class = sanitize_cls(use_class)
        if use_class not in REGISTER:
            raise ClsNotRegisteredException(f"class {str(use_class)} not in register")
        return REGISTER[use_class](instance, **kwargs)
    
    if instance is None:
        return None
    if isinstance(instance, (str, int, float)):
        if math.isnan(instance):
            return None
        return instance
    if isinstance(instance, (list, tuple)):
        return [instance_to_model(item) for item in instance]
    if isinstance(instance, dict):
        if not all([isinstance(key, str) for key in instance]):
            raise NonStrKeyException(f"Attempting to serialize dict with non str keys! {instance}")
        return {
            key: instance_to_model(value)
            for key, value in instance.items()
        }
    for Cls in instance.__class__.__mro__:
        if Cls in REGISTER:
            if Cls in skip_classes or any(issubclass(Cls, SkipCls) for SkipCls in skip_classes):
                continue
            return REGISTER[Cls](instance, **kwargs)
    raise ClsNotRegisteredException(f"class {instance.__class__}  has not been registered to be serialized!")


def serialize(Cls: Type[Any], pass_super_model: Dict[str, Any]=False, **kwargs):
    """Decorator function. Wrapping and registering serialization strategies.
    
    Args:
        Cls: Class to be serialized
        pass_super_model: flag if the serialized super class should be provided via `super_model_dict`
    """
    Cls = sanitize_cls(Cls)
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
