from .siibra_api_typing import ROLE_TYPE
from api.common import logger
from functools import wraps

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
                    
                bla = app.task(bind=True)(
                    wraps(
                        fn
                    )(celery_task_wrapper)
                )
                app.task()
                return bla
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
                async_result = func.apply_async(args, kwargs)
                return async_result.get()
            return_func = sync_get_result
        if return_func is None:
            raise NotImplementedError(f"router_decorator can only be used in roles: all, server, but you selected {role}")
        
        @wraps(fn)
        def inner(*args, **kwargs):
            return fn(*args, **kwargs, func=return_func)
        return inner
    return outer
