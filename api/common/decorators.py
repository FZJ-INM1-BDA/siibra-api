from functools import wraps, partial
import inspect
import asyncio
import time
from typing import Dict, Callable, Tuple

from .siibra_api_typing import ROLE_TYPE
from .logger import logger as general_logger
from .exceptions import (
    FaultyRoleException,
)

name_to_fns_map: Dict[str, Tuple[Callable, Callable]] = {}

def dummy(*args, **kwargs): pass

def data_decorator(role: ROLE_TYPE):
    """data decorator

    Extensively used in api.common.data_handlers. Most of the business logic, including data fetching, serialization, etc.
    
    Args:
        role: Role of this process
    
    Raises:
        ImportError: Celery not installed, but role is set to either `worker` or `server`
    """
    def outer_wrapper(fn):
        if role == "all":
            return fn
        if role == "worker" or role == "server":
            try:
                from api.worker import app
                
                def celery_task_wrapper(self, *args, **kwargs):
                    if role == "worker":
                        general_logger.info(f"Task Received: {fn.__name__=}, {args=}, {kwargs=}")
                    return fn(*args, **kwargs)
                    
                return app.task(bind=True)(
                    wraps(fn)(celery_task_wrapper)
                )
            except ImportError as e:
                errmsg = f"For worker role, celery must be installed as a dep"
                general_logger.critical(errmsg)
                raise ImportError(errmsg) from e
        raise FaultyRoleException(f"role must be 'all', 'server' or 'worker', but it is {role}")
    return outer_wrapper

def router_decorator(role: ROLE_TYPE, *, func, queue_as_async: bool=False, **kwargs):
    """Sync Router Decorator

    Args:
        role: role of this process
        func: function to be queued, or called, based on role
        queue_as_async: if set, will return id of the task, instead of task itself. Query the id for result.
    
    Raises:
        FaultyRoleException: if role is set to `all` and `queue_as_async` is set
        FaultyRoleException: if role is set to other than `all` or `server`
    """
    def outer(fn):

        global name_to_fns_map

        assert fn.__name__ not in name_to_fns_map, f"{fn.__name__} already in name_to_fns_map"
        name_to_fns_map[fn.__name__] = (fn, func)

        return_func = None
        if role == "all":
            if queue_as_async:
                raise FaultyRoleException(f"If role is set to all, cannot queue_as_async")
            return_func = func
        if role == "server":
            def sync_get_result(*args, **kwargs):
                if isinstance(func, partial):
                    func.func.s(*func.args, **func.keywords)
                    _func = func.func
                    args=[*args, *func.args]
                    kwargs={**kwargs, **func.keywords}
                else:
                    _func=func
                
                async_result = _func.apply_async(args, kwargs)
                if queue_as_async:
                    return async_result.id
                else:
                    return async_result.get()
            return_func = sync_get_result
        if return_func is None:
            raise FaultyRoleException(f"router_decorator can only be used in roles: all, server, but you selected {role}")
        
        @wraps(fn)
        def inner(*args, **kwargs):
            return fn(*args, **kwargs, func=return_func)
        return inner
    return outer

def async_router_decorator(role: ROLE_TYPE, *, func):
    """Async Router decorator

    Args:
        role: role of this process
        func: function to be queued, or called, based on role
    Raises:
        AssertionError: if wrapped function is not async
        TimeoutError: if the async process took more than 600sec to complete
        FaultyRoleException: if role is set to other than `all` or `server`
    """
    def outer(fn):
        global name_to_fns_map

        assert fn.__name__ not in name_to_fns_map, f"{fn.__name__} already in name_to_fns_map"
        name_to_fns_map[fn.__name__] = (fn, func)
        
        assert inspect.iscoroutinefunction(fn), f"async_router_decorator can only be used to decorate async functions"

        return_func = None
        if role == "all":
            async def async_get_direct_result(*args, **kwargs):
                return func(*args, **kwargs)
            return_func = async_get_direct_result
        if role == "server":
            async def async_get_result(*args, **kwargs):
                if isinstance(func, partial):
                    func.func.s(*func.args, **func.keywords)
                    _func = func.func
                    args=[*args, *func.args]
                    kwargs={**kwargs, **func.keywords}
                else:
                    _func=func
                
                async_result = _func.apply_async(args, kwargs)
                wait=0.1
                timestamp=time.time()
                while True:
                    if async_result.status == "SUCCESS":
                        return async_result.get()
                    if async_result.status == "FAILURE":
                        # on failure, getting the result will raise the exception
                        async_result.get()
                        raise Exception("unknown exception")
                    if (time.time() - timestamp) > 600:
                        async_result.revoke()
                        raise TimeoutError
                    await asyncio.sleep(wait)
                    wait = min(wait + wait, 1) # increase sleep duration, but at most 1 sec
            return_func = async_get_result

        if return_func is None:
            raise FaultyRoleException(f"router_decorator can only be used in roles: all, server, but you selected {role}")
        
        @wraps(fn)
        async def inner(*args, **kwargs):
            return await fn(*args, **kwargs, func=return_func)
        return inner
    return outer
