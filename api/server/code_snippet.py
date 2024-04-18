from ..common import NotFound, name_to_fns_map
from ..siibra_api_config import __version__
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi
from starlette.routing import Match, Route, Mount
from starlette.requests import Request
from starlette.types import Scope
from typing import Union, Iterable, Tuple
import json
from inspect import cleandoc
import re

CODE_RE = re.compile(r"```(?P<lang>.*?)\n(?P<code>[\w\W\s]*)\n```")
IGNORE_QUERY_KEYS = ("page", "size",)


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

def yield_codeblock(uncleandoc: str) -> Iterable[Tuple[str, str]]:
    
    doc = cleandoc(uncleandoc)
    matched_codeblock = CODE_RE.findall(doc)
    for codeblock_lang, codeblock_code in matched_codeblock:
        yield codeblock_lang, codeblock_code
    

def get_sourcecode(request: Request, lang: str="python") -> str:
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
    for codeblock_lang, codeblock_code in yield_codeblock(scope['endpoint'].__doc__):
        if codeblock_lang == lang:

            prefix = "\n".join([f"{key} = {json.dumps(value)}"
                                for key, value in ({
                                    **scope.get("path_params", {}),
                                    **dict(request.query_params),
                                }).items()
                                if key not in IGNORE_QUERY_KEYS])
            return f"{prefix}\n\n{codeblock_code}"
    raise NotFound

def add_sample_code(rootapp: FastAPI):
    app = rootapp
    
    def custom_api():
        if app.openapi_schema:
            return app.openapi_schema
            
        openapi_schema = get_openapi(
            title="siibra-api",
            version="v3",
            summary="siibra-api openapi specification",
            description="siibra-api is a http wrapper around siibra-python",
            routes=app.routes,
        )
        
        id_to_route = {
            route.operation_id or route.unique_id: route
            for route in app.routes
            if isinstance(route, APIRoute)
        }

        for path_value in openapi_schema.get("paths").values():
            for method_value in path_value.values():
                op_id = method_value.get("operationId")
                if op_id not in id_to_route:
                    continue
                route = id_to_route[op_id]
                if route.name not in name_to_fns_map:
                    continue
                fn0, fn1 = name_to_fns_map[route.name]
                method_value["x-codeSamples"] = [{
                    "lang": lang,
                    "source": code,
                } for lang, code in yield_codeblock(fn0.__doc__)]

        app.openapi_schema = openapi_schema
        return app.openapi_schema
    app.openapi = custom_api
