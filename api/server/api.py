from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from fastapi_versioning import VersionedFastAPI
import time
import json
from hashlib import md5

from .util import add_lazy_path

add_lazy_path()

from . import __version__, cache_header
from .cache import get_instance as get_cache_instance, terminate, on_startup
from .core import prefixed_routers as core_prefixed_routers
from .volumes import prefixed_routers as volume_prefixed_routers
from .compounds import prefixed_routers as compound_prefixed_routers
from .features import router as feature_router
from .metrics import prom_metrics_resp, on_startup as metrics_on_startup, on_terminate as metrics_on_terminate
from .code_snippet import get_sourcecode

from ..common import general_logger, access_logger, NotFound, SapiBaseException, name_to_fns_map
from ..siibra_api_config import GIT_HASH

siibra_version_header = "x-siibra-api-version"

siibra_api = FastAPI(
    title="siibra api",
    description="This is the REST api for siibra tools",
    version=__version__,
)

for prefix_router in [*core_prefixed_routers, *volume_prefixed_routers, *compound_prefixed_routers]:
    siibra_api.include_router(prefix_router.router, prefix=prefix_router.prefix)

siibra_api.include_router(feature_router, prefix="/feature")

add_pagination(siibra_api)

# Versioning for api endpoints
siibra_api = VersionedFastAPI(siibra_api)

templates = Jinja2Templates(directory="templates/")
siibra_api.mount("/static", StaticFiles(directory="static"), name="static")

# Allow Cors

origins = ["*"]
siibra_api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET"],
    expose_headers=[siibra_version_header]
)

# some plugins may strip origin header for privacy reasons
# so if origin is unavailable, append it to trick corsmiddleware to activate
@siibra_api.middleware("http")
async def append_origin_header(request: Request, call_next):
    headers = dict(request.scope["headers"])
    origin = request.headers.get("origin")
    new_headers = [(k, v) for k, v in headers.items()]
    if not origin:
        new_headers.append((b"origin", b"unknownorigin.dev"))
    request.scope["headers"] = new_headers
    return await call_next(request)

@siibra_api.get("/metrics", include_in_schema=False)
def get_metrics():
    """Get prometheus metrics"""
    return prom_metrics_resp()


@siibra_api.get("/ready", include_in_schema=False)
def get_ready():
    """Ready probe
    
    TODO: implement me"""
    return "ready"

@siibra_api.get("/", include_in_schema=False)
def get_home(request: Request):
    """Return the template for the siibra landing page."""
    return templates.TemplateResponse(
        "index.html", context={
            "request": request,
            "api_version": __version__,
            "git_hash": GIT_HASH,
            "versions": ["v3_0", "v2_0", "v1_0"]
        })

# Each middleware function is called before the request is processed
# For FastAPI the order is important.
# The functions are called (perhaps counter-intuitively) from bottom to top.
# See: https://github.com/encode/starlette/issues/479 and https://github.com/xgui3783/starlette-middleware-demo

async def read_bytes(generator) -> bytes:
    body = b""
    async for data in generator:
        body += data
    return body


do_not_cache_list = [
    "metrics",
    "openapi.json",
    "atlas_download"
]

do_no_cache_query_list = [
    "bbox=",
    "find="
]

do_not_logs = (
    "/ready",
    "/metrics",
)


@siibra_api.middleware("http")
async def middleware_cache_response(request: Request, call_next):
    """Cache requests to redis, to improve response time."""
    cache_instance = get_cache_instance()

    hashed_path = md5(f"{request.url.path}{str(request.url.query)}".encode("utf-8")).hexdigest()
    cache_key = f"[{__version__}] {hashed_path}"

    auth_set = request.headers.get("Authorization") is not None

    accept_header = request.headers.get("Accept")
    query_code_flag = accept_header == "text/x-sapi-python"

    # bypass cache set if:
    # - method is not GET
    # - if auth token is set
    # - if any part of request.url.path matches with do_not_cache_list
    # - if any keyword appears in do_no_cache_query_list
    bypass_cache_set = (
        request.method.upper() != "GET"
        or auth_set
        or query_code_flag
        or any (keyword in request.url.path for keyword in do_not_cache_list)
        or any (keyword in request.url.query for keyword in do_no_cache_query_list)
    )

    # bypass cache read if:
    # - bypass cache set
    # - x-bypass-fastapi-cache is present
    bypass_cache_read = (
        request.headers.get("x-bypass-fastapi-cache")
    ) or bypass_cache_set

    # starlette seems to normalize header to lower case
    # so .get("origin") also works if the request has "Origin: http://..."

    # N.B. do not append cors header based on origin
    # some plugins may strip origin header for privacy reasons
    # has_origin = request.headers.get("origin")
    extra_headers = {
        "access-control-allow-origin": "*",
        "access-control-expose-headers": f"{siibra_version_header}",
        siibra_version_header: __version__,
    }

    cached_value = cache_instance.get_value(cache_key) if not bypass_cache_read else None

    status_code_key = "status_code"

    if cached_value:
        loaded_value = json.loads(cached_value)
        if loaded_value.get("error"):
            status_code = loaded_value.get(status_code_key, 500)
        else:
            status_code = 200
        return Response(
            cached_value,
            status_code=status_code,
            headers={
                "content-type": "application/json",
                cache_header: "hit",
                **extra_headers,
            }
        )

    
    try:
        response = await call_next(request)
        status_code = 200
        response_content_type = response.headers.get("content-type")
        response_headers = response.headers
        content = await read_bytes(response.body_iterator)

        if response.status_code == 404:
            status_code = 404
            response_content_type = "application/json"
            content = json.dumps({
                "error": True,
                status_code_key: status_code,
                "message": content.decode()
            }).encode("utf-8")
            response_headers = extra_headers

        elif response.status_code >= 400:
            status_code = response.status_code
            response_content_type = None
            content = json.dumps({
                "error": True,
                status_code_key: status_code,
                "message": content.decode()
            }).encode("utf-8")
            response_headers = extra_headers
        
    except NotFound as e:
        status_code = 404
        response_content_type = "application/json"
        content = json.dumps({
            "error": True,
            status_code_key: status_code,
            "message": str(e)
        }).encode("utf-8")
        response_headers = extra_headers
    except Exception as e:
        status_code = 500
        response_content_type = None
        content = json.dumps({
            "error": True,
            status_code_key: status_code,
            "message": str(e)
        }).encode("utf-8")
        response_headers = extra_headers
        

    # conditions when do not cache
    if (not bypass_cache_set) and response_content_type == "application/json":
        cache_instance.set_value(cache_key, content)
    return Response(
        content,
        status_code=status_code,
        headers=response_headers
    )



@siibra_api.middleware("http")
async def middleware_get_python_code(request: Request, call_next):
    """If Accept header is set to text/x-sapi-python, return the python code as plain text response."""
    accept_header = request.headers.get("Accept")

    if accept_header == "text/x-sapi-python":
        try:
            src = get_sourcecode(request)
            return PlainTextResponse(src)
        except NotFound as e:
            return PlainTextResponse(str(e), 404)
    
    return await call_next(request)

@siibra_api.middleware("http")
async def middleware_add_version_header(request: Request, call_next):
    """Add siibra-api version as a custom header"""
    response = await call_next(request)
    response.headers[siibra_version_header] = __version__
    return response

@siibra_api.middleware("http")
async def middleware_access_log(request: Request, call_next):
    """Access log middleware"""
    
    if request.url.path in do_not_logs:
        return await call_next(request)
    
    start_time = time.time()
    try:
        resp = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        access_logger.info(f"{request.method.upper()} {str(request.url)}", extra={
            "resp_status": str(resp.status_code),
            "process_time_ms": str(round(process_time)),
            "hit_cache": "cache_hit" if resp.headers.get(cache_header) == "hit" else "cache_miss"
        })
        return resp
    
    # Reverse proxy sometimes has a dedicated timeout
    # In events where server takes too long to respond, fastapi will raise a RuntimeError with body "No response returned."
    # Log the incident, and the time of response (This should reflect the duration of request, rather than when the client closes the connection)
    except RuntimeError:
        process_time = (time.time() - start_time) * 1000
        access_logger.info(f"{request.method.upper()} {str(request.url)}", extra={
            "resp_status": "504",
            "process_time_ms": str(round(process_time)),
            "hit_cache": "cache_miss"
        })
    except Exception as e:
        general_logger.critical(e)

@siibra_api.exception_handler(RuntimeError)
async def exception_runtime(request: Request, exc: RuntimeError) -> JSONResponse:
    """Handling RuntimeErrors.
    Most of the RuntimeErrors are thrown by the siibra-python library when other Services are not responding.
    To be more resilient and not throw a simple and unplanned HTTP 500 response, this handler will return an HTTP 503
    status."""
    general_logger.warning(f"Error handler: exception_runtime: {str(exc)}")
    return JSONResponse(
        status_code=503,
        content={
            "detail": "This part of the siibra service is temporarily unavailable",
            "error": str(exc)
        },
    )

@siibra_api.exception_handler(SapiBaseException)
def exception_sapi(request: Request, exc: SapiBaseException):
    """Handle sapi errors"""
    general_logger.warning(f"Error handler: exception_sapi: {str(exc)}")
    raise HTTPException(400, str(exc))

@siibra_api.exception_handler(Exception)
async def exception_other(request: Request, exc: Exception):
    """Catch all exception handler"""
    general_logger.warning(f"Error handler: exception_other: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Some error occurred",
            "error": str(exc)
        }
    )

@siibra_api.on_event("shutdown")
def shutdown():
    """On shutdown"""
    terminate()
    metrics_on_terminate()

@siibra_api.on_event("startup")
def startup():
    """On startup"""
    on_startup()
    metrics_on_startup()

import logging
class EndpointLoggingFilter(logging.Filter):
    """Custom logger filter. Do not log metrics, ready endpoint."""
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return all(
            message.find(do_not_log) == -1 for do_not_log in do_not_logs
        )

logging.getLogger("uvicorn.access").addFilter(EndpointLoggingFilter())
