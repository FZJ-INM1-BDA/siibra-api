# Copyright 2018-2020 Institute of Neuroscience and Medicine (INM-1),
# Forschungszentrum Jülich GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import requests
import siibra
import uuid
import hashlib
from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi_versioning import VersionedFastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from app.core.siibra_api import router as siibra_router
from app.core.atlas_api import router as atlas_router
from app.service.health import router as health_router
from app.service.metrics import router as metrics_router

from app.configuration.ebrains_token import get_public_token
from app.configuration.siibra_custom_exception import SiibraCustomException
from app.configuration.cache_redis import CacheRedis
from . import logger
from . import __version__
import logging

siibra.logger.setLevel(logging.WARNING)

security = HTTPBearer()

# Tags to structure the api documentation
tags_metadata = [
    {
        "name": "atlases",
        "description": "Atlas related data",
    },
    {
        "name": "parcellations",
        "description": "Parcellations related data, depending on selected atlas",
    },
    {
        "name": "spaces",
        "description": "Spaces related data, depending on selected atlas",
    },
    {
        "name": "data",
        "description": "Further information like, genes, features, ...",
    },
]

ATLAS_PATH = '/atlases'
siibra_version_header = 'x-siibra-api-version'

# Main fastAPI application
app = FastAPI(
    title="Siibra API",
    description="This is the REST api for siibra tools",
    version="1.0",
    openapi_tags=tags_metadata
)

app.include_router(atlas_router)
app.include_router(siibra_router)
app.include_router(health_router)
app.include_router(metrics_router)

# Versioning for all api endpoints
app = VersionedFastAPI(app, default_api_version=1)

# Template list, with every template in the project
# can be rendered and returned
templates = Jinja2Templates(directory='templates/')
app.mount("/static", StaticFiles(directory="static"), name="static")


# Allow CORS
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['GET'],
    expose_headers=[siibra_version_header]
)


@app.get('/', include_in_schema=False)
def home(request: Request):
    """
    Return the template for the siibra landing page.

    :param request: fastApi Request object
    :return: the rendered index.html template
    """
    return templates.TemplateResponse(
        'index.html', context={
            'request': request})




# Each middleware function is called before the request is processed
# For FastAPI the order is important.
# The functions are called from bottom to top.

async def read_bytes(generator) -> bytes:
    body = b""
    async for data in generator:
        body += data
    return body


@app.middleware("http")
async def cache_response(request: Request, call_next):
    """
    Cache requests to redis, to improve response time.

    Cached content is returned with a new response. In this NO other following middleware will be called

    :param request: current request
    :param call_next: next middleware function
    :return: current response or a new Response with cached content
    """
    redis = CacheRedis.get_instance()

    cache_key = f"[{__version__}] {request.url.path}{str(request.url.query)}"

    auth_set = request.headers.get('Authorization') is not None

    # bypass cache read if:
    # - method is not GET
    # - x-bypass-fast-api-cache is present
    # - if auth token is set
    bypass_cache_read = request.method.upper() != "GET" or request.headers.get(
        "x-bypass-fast-api-cache") or auth_set or 'metrics' in request.url.path

    # bypass cache set if:
    # - method is not GET
    # - if auth token is set
    bypass_cache_set = request.method.upper() != "GET" or auth_set

    cached_value = redis.get_value(cache_key) if not bypass_cache_read else None
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
    redis.set_value(cache_key, content)
    return Response(
        content,
        headers=response.headers
    )


@app.middleware('http')
async def set_auth_header(request: Request, call_next):
    """
    Set authentication for further requests with siibra
    If a user provides a header, this one will be used otherwise use the default public token
    :param request: current request
    :param call_next: next middleware function
    :return: an altered response
    """

    bearer_token = request.headers.get('Authorization')
    try:
        if bearer_token:
            siibra.set_ebrains_token(bearer_token.replace('Bearer ', ''))
        else:
            public_token = get_public_token()
            siibra.set_ebrains_token(public_token)
        response = await call_next(request)
        return response
    except SiibraCustomException as err:
        logger.error('Could not set authentication token')
        return JSONResponse(
            status_code=err.status_code, content={
                'message': err.message})


@app.middleware('http')
async def add_version_header(request: Request, call_next):
    """
    Add the latest application version as a custom header
    """
    response = await call_next(request)
    response.headers[siibra_version_header] = __version__
    return response


@app.middleware('http')
async def matomo_request_log(request: Request, call_next):
    """
    Middleware will be executed before each request.
    If the URL does not belong to a resource file, a log will be sent to matomo monitoring.
    :param request: current fastAPI request object
    :param call_next: next middleware method
    :return: the response after preprocessing
    """
    test_url = request.url
    test_list = ['.css', '.js', '.png', '.gif', '.json', '.ico', 'localhost']
    res = any(ele in str(test_url) for ele in test_list)

    if 'SIIBRA_ENVIRONMENT' in os.environ:
        # if os.environ['SIIBRA_ENVIRONMENT'] == 'PRODUCTION':
        if not res:
            payload = {
                'idsite': 13,
                'rec': 1,
                'action_name': 'siibra_api',
                'url': request.url,
                '_id': hashlib.blake2b(digest_size=8, key=request.client.host.encode()).hexdigest(),
                'rand': str(uuid.uuid1()),
                'lang': request.headers.get('Accept-Language'),
                'ua': request.headers.get('User-Agent'),
                '_cvar': {'1': ['environment', os.environ['SIIBRA_ENVIRONMENT']]}
            }
            print(payload)
            try:
                r = requests.get('https://stats.humanbrainproject.eu/matomo.php', params=payload)
                print('Matomo logging with status: {}'.format(r.status_code))
                pass
            except Exception:
                logger.info('Could not log to matomo instance')
        else:
            logger.info('Request for: {}'.format(request.url))
    response = await call_next(request)
    return response


@app.get('/ready', include_in_schema=False)
def get_ready():
    return 'OK'