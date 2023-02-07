from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from fastapi_versioning import VersionedFastAPI
import time

from .util import add_lazy_path

add_lazy_path()

from . import __version__
from .cache import get_instance as get_cache_instance, terminate, on_startup
from .core import prefixed_routers as core_prefixed_routers
from .volumes import prefixed_routers as volume_prefixed_routers
from .features import router as feature_router

from api.common import logger, access_logger, AmbiguousParameters, InsufficientParameters

siibra_version_header = "x-siibra-api-version"

siibra_api = FastAPI(
    title="siibra api",
    description="This is the REST api for siibra tools",
    version=__version__,
)

for prefix_router in [*core_prefixed_routers, *volume_prefixed_routers]:
    siibra_api.include_router(prefix_router.router, prefix=prefix_router.prefix)

siibra_api.include_router(feature_router, prefix="/feature")

# add pagination
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

@siibra_api.get("/ready", include_in_schema=False)
def ready():
    # TODO ready probe
    return "ready"

@siibra_api.get("/", include_in_schema=False)
def home(request: Request):
    """
    Return the template for the siibra landing page.

    :param request: fastApi Request object
    :return: the rendered index.html template
    """
    return templates.TemplateResponse(
        "index.html", context={
            "request": request,
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
    "openapi.json"
]

do_no_cache_query_list = [
    "bbox="
]

do_not_logs = (
    "/ready",
)


@siibra_api.middleware("http")
async def cache_response(request: Request, call_next):
    """
    Cache requests to redis, to improve response time.

    Cached content is returned with a new response. In this NO other following middleware will be called

    :param request: current request
    :param call_next: next middleware function
    :return: current response or a new Response with cached content
    """
    cache_instance = get_cache_instance()

    cache_key = f"[{__version__}] {request.url.path}{str(request.url.query)}"

    auth_set = request.headers.get("Authorization") is not None

    # bypass cache read if:
    # - method is not GET
    # - x-bypass-fast-api-cache is present
    # - if auth token is set
    # - if any part of request.url.path matches with do_not_cache_list
    bypass_cache_read = (
        request.method.upper() != "GET"
        or request.headers.get("x-bypass-fast-api-cache")
        or auth_set
        or any (keyword in request.url.path for keyword in do_not_cache_list)
        or any (keyword in request.url.query for keyword in do_no_cache_query_list)
    )

    # bypass cache set if:
    # - method is not GET
    # - if auth token is set
    # - if any part of request.url.path matches with do_not_cache_list
    bypass_cache_set = (
        request.method.upper() != "GET" 
        or auth_set 
        or any (keyword in request.url.path for keyword in do_not_cache_list)
    )
    cached_value = cache_instance.get_value(cache_key) if not bypass_cache_read else None
    if cached_value:
        # starlette seems to normalize header to lower case
        # so .get("origin") also works if the request has "Origin: http://..."
        has_origin = request.headers.get("origin")
        extra_headers = {
            "access-control-allow-origin": "*",
            "access-control-expose-headers": f"{siibra_version_header}",
            siibra_version_header: __version__,
        } if has_origin else {}

        return Response(
            cached_value,
            headers={
                "content-type": "application/json",
                "x-fastapi-cache": "hit",
                **extra_headers,
            }
        )

    response = await call_next(request)

    # conditions when do not cache
    if (
            bypass_cache_set or
            response.status_code >= 400 or
            response.headers.get("content-type") != "application/json"
    ):
        return response

    content = await read_bytes(response.body_iterator)
    cache_instance.set_value(cache_key, content)
    return Response(
        content,
        headers=response.headers
    )


@siibra_api.middleware("http")
async def add_version_header(request: Request, call_next):
    """
    Add the latest application version as a custom header
    """
    response = await call_next(request)
    response.headers[siibra_version_header] = __version__
    return response

@siibra_api.middleware("http")
async def access_log(request: Request, call_next):
    
    if request.url.path in do_not_logs:
        return await call_next(request)
    
    start_time = time.time()
    try:
        resp = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        access_logger.info(f"{request.method.upper()} {str(request.url)}", extra={
            "resp_status": str(resp.status_code),
            "process_time_ms": str(round(process_time)),
            "hit_cache": "cache_hit" if resp.headers.get("x-fastapi-cache") == "hit" else "cache_miss"
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
        logger.critical(e)

@siibra_api.exception_handler(RuntimeError)
async def runtime_exception_handler(request: Request, exc: RuntimeError):
    """
    Handling RuntimeErrors.
    Most of the RuntimeErrors are thrown by the siibra-python library when other Services are not responding.
    To be more resilient and not throw a simple and unplanned HTTP 500 response, this handler will return an HTTP 503
    status.
    :param request: Needed but fastapi definition, but not used
    :param exc: RuntimeError
    :return: HTTP status 503 with a custom message
    """
    logger.warning(f"Runtime Error: {str(exc)}")
    return JSONResponse(
        status_code=503,
        content={
            "detail": "This part of the siibra service is temporarily unavailable",
            "error": str(exc)
        },
    )

@siibra_api.exception_handler(InsufficientParameters)
def insufficent_argument(request: Request, exc: InsufficientParameters):
    raise HTTPException(400, str(exc))

@siibra_api.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    logger.warning(f"Exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Some error occurred",
            "error": str(exc)
        }
    )

@siibra_api.on_event("shutdown")
def shutdown():
    terminate()

@siibra_api.on_event("startup")
def startup():
    on_startup()

import logging
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return all(
            message.find(do_not_log) == -1 for do_not_log in do_not_logs
        )

logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
