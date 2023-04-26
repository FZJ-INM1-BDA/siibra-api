from .siibra_api_typing import ROLE_TYPE
from api.common import logger
from functools import wraps, partial
import inspect
import asyncio
import time

def dummy(*args, **kwargs): pass

def data_decorator(role: ROLE_TYPE):
    def outer_wrapper(fn):
        if role == "all":
            return fn
        if role == "worker" or role == "server":
            try:
                from api.worker import app
                
                def celery_task_wrapper(self, *args, **kwargs):
                    return fn(*args, **kwargs)
                    
                return app.task(bind=True)(
                    wraps(fn)(celery_task_wrapper)
                )
            except ImportError as e:
                errmsg = f"For worker role, celery must be installed as a dep"
                print(errmsg)
                logger.critical(errmsg)
                raise NotImplementedError(e)
        # TODO, perhaps use 'all' as a fallback?
        raise RuntimeError(f"role must be 'all', 'server' or 'worker', but it is {role}")
    return outer_wrapper

def router_decorator(role: ROLE_TYPE, *, func):
    def outer(fn):

        return_func = None
        if role == "all":
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
                return async_result.get()
            return_func = sync_get_result
        if return_func is None:
            raise NotImplementedError(f"router_decorator can only be used in roles: all, server, but you selected {role}")
        
        @wraps(fn)
        def inner(*args, **kwargs):
            return fn(*args, **kwargs, func=return_func)
        return inner
    return outer

def async_router_decorator(role: ROLE_TYPE, *, func):
    def outer(fn):
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
                    if (time.time() - timestamp) > 60:
                        raise TimeoutError
                    await asyncio.sleep(wait)
                    wait = min(wait + wait, 1) # increase sleep duration, but at most 1 sec
            return_func = async_get_result

        if return_func is None:
            raise NotImplementedError(f"router_decorator can only be used in roles: all, server, but you selected {role}")
        
        @wraps(fn)
        async def inner(*args, **kwargs):
            return await fn(*args, **kwargs, func=return_func)
        return inner
    return outer
