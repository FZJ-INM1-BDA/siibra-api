from functools import wraps, partial
from inspect import signature

from fastapi import APIRouter
from fastapi_versioning import version
from typing import Type, List

from api.server.util import SapiCustomRoute
from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.common import router_decorator

TAGS= ["feature"]

router = APIRouter(route_class=SapiCustomRoute, tags=TAGS)

def wrap_feature_type(feature_type: str, *, path:str, response_model: Type, tags: List[str]=[], func=lambda:[]):
    def outer(fn):

        @router.get(f"/{feature_type}{path}", response_model=response_model, tags=tags)
        @version(*FASTAPI_VERSION)
        @router_decorator(ROLE, func=partial(func, type=feature_type))
        @wraps(fn)
        def inner(*args, **kwargs):
            return fn(*args, **kwargs)
        return inner
    return outer

def wrap_feature_catetory(feature_category: str, *, path: str, response_model: Type, tags: List[str]=[], func=lambda:[]):
    def outer(fn):

        # if type is not present in original fn, do not add as kwarg
        pass_type_flag = "type" in signature(fn).parameters

        @router.get(f"/{feature_category}{path}", response_model=response_model, tags=tags)
        @version(*FASTAPI_VERSION)
        @router_decorator(ROLE, func=func)
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
