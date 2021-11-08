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
import json
import siibra
from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

from fastapi_versioning import VersionedFastAPI

from app.core.siibra_api import router as siibra_router
from app.core.atlas_api import router as atlas_router
from app.service.health import router as health_router
from app.configuration.ebrains_token import get_public_token
from app.configuration.siibra_custom_exception import SiibraCustomException
from . import logger
from . import __version__
import logging
import re
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
        "name": "regions",
        "description": "Regions related data, deepnds on selected atlas and parcellation.",
    },
    {
        "name": "spaces",
        "description": "Spaces related data, depending on selected atlas",
    },
    {
        "name": "data",
        "description": "Further information like, genes, features, ...",
    },
    {
        "name": "features",
        "description": "All feature related queries",
    },
]

ATLAS_PATH = '/atlases'
siibra_version_header='x-siibra-api-version'

# Main fastAPI application
app = FastAPI(
    title="Siibra API",
    description="This is the REST api for siibra tools",
    version=__version__,
    openapi_tags=tags_metadata
)
# Add a siibra router with further endpoints
app.include_router(atlas_router)
app.include_router(siibra_router)
app.include_router(health_router)


# Versioning for all api endpoints
app = VersionedFastAPI(app, default_api_version=1)

def patch_code_samples():

    fallback_lang = 'shell'

    host_url = os.environ.get('HOSTURL', 'http://localhost:5000')
    code_sample_key = 'x-code-samples'
    code_sample_re = re.compile(r'^## code sample', re.M)
    get_samples_re = re.compile(r'^```(.+)?\n(?:.*\n)+?^```$', re.M)
    preceding_nl_re = re.compile(r'^\n*', re.M)
    trailing_nl_re = re.compile(r'\n*$', re.M)
    
    # Customise open-api
    def patch_openapi(target_app: FastAPI, target_path: str):
        
        def custom_openapi():
            if target_app is None:
                raise NotImplementedError(f'path for {target_path} not yet implemented')
            if target_app.openapi_schema:
                return target_app.openapi_schema
            openapi_schema = get_openapi(
                title='siibra-api',
                routes=target_app.routes,
                description='openapi for siibra-api',
                version=__version__,
                servers=[{
                    'url': f'{target_path}'
                }]
            )

            # patch the logo
            openapi_schema['info']['x-logo'] = {
                'url': 'https://raw.githubusercontent.com/FZJ-INM1-BDA/siibra-api/master/static/images/siibra-api.jpeg'
            }

            # extract summary, description and code sample from doc strings
            for path_key in openapi_schema['paths']:
                for method in openapi_schema['paths'][path_key]:
                    description:str = openapi_schema['paths'][path_key][method].get('description')

                    # if docstring is not provided, skip
                    if not description:
                        continue

                    description = re.sub(preceding_nl_re, '', description)
                    if description[0] == '#':
                        summary, desc = description.split('\n',maxsplit=1)
                        summary = re.sub(r'^(#\s)+',  '', summary)
                        desc = re.sub(r'^\n*', '', desc, flags=re.M)
                    else:
                        summary = None
                        desc = description
                    split_desc = re.split(code_sample_re, desc)
                    if len(split_desc) > 1:
                        desc_body, code_snippit = split_desc
                        for code_sample in get_samples_re.finditer(code_snippit):

                            if code_sample_key not in openapi_schema['paths'][path_key][method]:
                                openapi_schema['paths'][path_key][method][code_sample_key] = []

                            lang, = code_sample.groups()
                            md_code_sample = code_sample.group()
                            md_code_sample = '\n'.join([line for line in md_code_sample.split('\n') if line[0:3] != '```'])
                            openapi_schema['paths'][path_key][method][code_sample_key].append({
                                'lang': lang or fallback_lang,
                                'source': md_code_sample
                            })

                        # append curl... because why not?
                        openapi_schema['paths'][path_key][method][code_sample_key].append({
                            'lang': 'shell',
                            'source': f'curl {host_url}{target_path}{path_key.replace("{", "${")}'
                        })
                    else:
                        desc_body = desc

                    desc_body = re.sub(trailing_nl_re, '', desc_body)
                    openapi_schema['paths'][path_key][method]['description'] = desc_body
                    if summary is not None:
                        openapi_schema['paths'][path_key][method]['summary'] = summary
                
            target_app.openapi_schema = openapi_schema
            return openapi_schema
        
        return custom_openapi

    target_routes = ['/v1_0']
    for route in [route for route in app.routes if route.path in target_routes]:
        target_app: FastAPI = route.app
        target_app.openapi = patch_openapi(target_app, route.path)

patch_code_samples()


# Template list, with every template in the project
# can be rendered and returned
templates = Jinja2Templates(directory='templates/')
app.mount("/static", StaticFiles(directory="static"), name="static")

pypi_stat_url = 'https://pypistats.org/api/packages/siibra/overall?mirrors=false'

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


@app.get('/stats', include_in_schema=False)
def home(request: Request):
    """
    Return the template for the siibra statistics.

    :param request: fastApi Request object
    :return: the rendered stats.html template
    """
    download_data_json = requests.get(pypi_stat_url)
    if download_data_json.status_code == 200:
        download_data = json.loads(download_data_json.content)

        download_sum = 0
        download_sum_month = {}

        for d in download_data['data']:
            download_sum += d['downloads']
            date_index = '{}-{}'.format(d['date'].split('-')
                                        [0], d['date'].split('-')[1])
            if date_index not in download_sum_month:
                download_sum_month[date_index] = 0
            download_sum_month[date_index] += d['downloads']

        return templates.TemplateResponse('stats.html', context={
            'request': request,
            'download_sum': download_sum,
            'download_sum_month': download_sum_month
        })
    else:
        logger.warning('Could not retrieve pypi statistics')
        raise HTTPException(status_code=500,
                            detail='Could not retrieve pypi statistics')


@app.middleware('http')
async def set_auth_header(request: Request, call_next):
    """
    Set authentication for further requests with siibra
    If a user provides a header, this one will be used otherwise use the default public token
    :param request: current request
    :param call_next: next middleware function
    :return: an altered response
    """

    path = request.scope['path']  # get the request route
    print(f'path: {path}')

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
async def matomo_request_log(request: Request, call_next):
    """
    Middleware will be executed before each request.
    If the URL does not belog to a resource file, a log will be send to matomo monitoring.
    :param request: current fastAPI request object
    :param call_next: next middleware method
    :return: the response after preprocessing
    """
    test_url = request.url
    test_list = ['.css', '.js', '.png', '.gif', '.json', '.ico']
    res = any(ele in str(test_url) for ele in test_list)

    if 'SIIBRA_ENVIRONMENT' in os.environ:
        if os.environ['SIIBRA_ENVIRONMENT'] == 'PRODUCTION':
            if not res:
                payload = {
                    'idsite': 13,
                    'rec': 1,
                    'action_name': 'siibra_api',
                    'url': request.url,
                    '_id': 'my_ip',
                    'lang': request.headers.get('Accept-Language'),
                    'ua': request.headers.get('User-Agent')
                }
                try:
                    # r = requests.get('https://stats.humanbrainproject.eu/matomo.php', params=payload)
                    # print('Matomo logging with status: {}'.format(r.status_code))
                    pass
                except Exception:
                    logger.info('Could not log to matomo instance')
        else:
            logger.info('Request for: {}'.format(request.url))
    response = await call_next(request)
    return response

@app.middleware('http')
async def add_version_header(request: Request, call_next):
    response = await call_next(request)
    response.headers[siibra_version_header] = __version__
    return response

@app.get('/ready', include_in_schema=False)
def get_ready():
    return 'OK'


@app.on_event('startup')
async def on_startup():
    pass