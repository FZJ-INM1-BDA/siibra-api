from functools import wraps
from inspect import signature, iscoroutinefunction


def wrap_feature_category(feature_category: str):
    """Wrap feature category
    
    Args:
        feature_category: string representing the type to be passed as keyword argument
    """
    def outer(fn):
        
        pass_type_flag = "type" in signature(fn).parameters
        """if type is not present in original fn, do not add as kwarg"""
        
        if iscoroutinefunction(fn):
            @wraps(fn)
            async def inner(*args, **kwargs):
                if not pass_type_flag:
                    return await fn(*args, **kwargs)
                
                # If type not added as kwarg, assuming wanting all feature from said category
                # hence add feature_category as type
                if "type" not in kwargs or kwargs["type"] is None:
                    kwargs["type"] = feature_category
                return await fn(*args, **kwargs)
        else:
            @wraps(fn)
            def inner(*args, **kwargs):
                if not pass_type_flag:
                    return fn(*args, **kwargs)
                
                # If type not added as kwarg, assuming wanting all feature from said category
                # hence add feature_category as type
                if "type" not in kwargs or kwargs["type"] is None:
                    kwargs["type"] = feature_category
                return fn(*args, **kwargs)
        return inner
    return outer
