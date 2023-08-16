from ..common import name_to_fns_map, NotFound
from fastapi import FastAPI
from starlette.routing import Match, Route, Mount
from starlette.requests import Request
from starlette.types import Scope
from typing import Union, Callable, List, Tuple, Dict
import json
from inspect import unwrap, getsource
from functools import partial

target_fn_names = (
    "async_get_direct_result",
    "async_get_result",
    "sync_get_result"
)

globals_to_retrieve = {
    "_get_all_features": [
        "_get_all_features",
        "extract_concept",
        "InsufficientParameters",
    ]
}

def get_source_from_fn(fn: Callable) -> Tuple[str, str, List[str], Dict[str, str]]:
    """Gets the all functions in a closure"""

    args = []
    kwargs = {}
    if "feature_category" in fn.__code__.co_freevars:
        kwargs["type"] = dict(zip(fn.__code__.co_freevars, [c.cell_contents for c in fn.__closure__]))["feature_category"]

    assert fn.__name__ in name_to_fns_map
    fn0, fn1 = name_to_fns_map[fn.__name__]

    if isinstance(fn1, partial):
        src = getsource(fn1.func)
        func_name = fn1.func.__name__
        args = [*args, *fn1.args]
        kwargs = {**kwargs, **fn1.keywords}

        target_fn = unwrap(fn1.func)
    else:
        src = getsource(fn1)
        func_name = fn1.__name__
        target_fn = unwrap(fn1)


    src = src.replace("@data_decorator(ROLE)", "")
    _globals = {
        _global
        for key, _globals in globals_to_retrieve.items()
        if key in src
        for _global in _globals
    }

    for _global in _globals:
        assert _global in target_fn.__globals__, f"expecting {_global} to be in globals, but was not"
        global_func = target_fn.__globals__[_global]
        global_src = getsource(global_func)
        src = f"""\n{global_src}\n{src}\n"""
        
    return src, func_name, fn1.args, fn1.keywords


def lookup_handler_fn(arm: Union[FastAPI, Mount, Route], scope: Scope):
    """Lookup (recursively if necessary) to find the Route responsible for a given scope."""
    if isinstance(arm, (FastAPI, Mount)):
        for route in arm.routes:
            match, child_scope = route.matches(scope)
            if match == Match.FULL:
                child_match = lookup_handler_fn(route, { **scope, **child_scope })
                if child_match:
                    return child_match
    if isinstance(arm, Route):
        match, child_scope = arm.matches(scope)
        if match == Match.FULL:
            return arm, child_scope
    return None

def get_sourcecode(request: Request) -> str:
    """Process a request, and transform it into the corresponding Python snippet
    
    Args:
        request: Request
    
    Returns:
        python snippet
    
    Raises:
        NotFound
    """
    
    returned_val = lookup_handler_fn(request.app, request.scope)
    if not returned_val:
        raise NotFound("handler_fn lookup failed!")
    
    arm, scope = returned_val

    source, fn_name, args, kwargs = get_source_from_fn(arm.endpoint)
    
    ignore_keys = ("page", "size",)
    kwargs = {
        **kwargs,
        **{
            key: value
            for key, value in ({
                **dict(request.query_params),
                **scope.get("path_params")
            }).items()
            if key not in ignore_keys
        }
    }
    args = [*args]
    
    header = f"""args={json.dumps(args, indent=2)}\nkwargs={json.dumps(kwargs, indent=2)}\n\n"""
    footer = f"\n\n{fn_name}(*args, **kwargs)\n\n"

    return f"{header}{source}{footer}"
