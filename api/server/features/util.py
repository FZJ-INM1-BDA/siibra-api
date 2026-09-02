from functools import wraps
from inspect import signature, iscoroutinefunction

from api.common.data_handlers import overrides

def wrap_feature_category(feature_category: str):
    """Wrap feature category
    
    Args:
        feature_category: string representing the type to be passed as keyword argument
    """

    extra_items = [
        overrides.cleanup_item(item)
        for item in overrides.override_items
        if (
            item.get("_type") == "_features"
            and item.get("_feature") == feature_category
        )
    ]
    def outer(fn):
        
        pass_type_flag = "type" in signature(fn).parameters
        """if type is not present in original fn, do not add as kwarg"""
        
        if iscoroutinefunction(fn):
            @wraps(fn)
            async def inner(*args, **kwargs):
                if not pass_type_flag:
                    result = await fn(*args, **kwargs)
                
                # If type not added as kwarg, assuming wanting all feature from said category
                # hence add feature_category as type
                if "type" not in kwargs or kwargs["type"] is None:
                    kwargs["type"] = feature_category
                result = await fn(*args, **kwargs)
                if isinstance(result, list):
                    result.extend(extra_items)
                return result
        else:
            @wraps(fn)
            def inner(*args, **kwargs):
                if not pass_type_flag:
                    result = fn(*args, **kwargs)
                
                # If type not added as kwarg, assuming wanting all feature from said category
                # hence add feature_category as type
                if "type" not in kwargs or kwargs["type"] is None:
                    kwargs["type"] = feature_category
                result = fn(*args, **kwargs)
                if isinstance(result, list):
                    result.extend(extra_items)
                return result
        return inner
    return outer
