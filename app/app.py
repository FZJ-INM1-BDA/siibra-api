# Copyright 2018-2020 Institute of Neuroscience and Medicine (INM-1), Forschungszentrum Jülich GmbH

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
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from siibra.ebrains import Authentication
from fastapi_versioning import VersionedFastAPI

from .siibra_api import router as siibra_router
from .atlas_api import router as atlas_router
from .space_api import router as space_router
from .parcellation_api import router as parcellation_router
from .ebrains_token import get_public_token


security = HTTPBearer()

# Main fastAPI application
app = FastAPI()
# Add a siibra router with further endpoints
app.include_router(parcellation_router)
app.include_router(space_router)
app.include_router(atlas_router)
app.include_router(siibra_router)

# Versioning for all api endpoints
app = VersionedFastAPI(app, default_api_version=1)

# Template list, with every template in the project
# can be rendered and returned
templates = Jinja2Templates(directory='app/templates/')

pypi_stat_url = 'https://pypistats.org/api/packages/siibra/overall?mirrors=false'

# Allow CORS
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['GET'],
)


@app.get('/')
def home(request: Request):
    """
    Return the template for the siibra landing page.

    :param request: fastApi Request object
    :return: the rendered index.html template
    """
    return templates.TemplateResponse('index.html', context={'request': request})


@app.get('/stats')
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
            date_index = '{}-{}'.format(d['date'].split('-')[0], d['date'].split('-')[1])
            if date_index not in download_sum_month:
                download_sum_month[date_index] = 0
            download_sum_month[date_index] += d['downloads']

        return templates.TemplateResponse('stats.html', context={
            'request': request,
            'download_sum': download_sum,
            'download_sum_month': download_sum_month
        })
    else:
        raise HTTPException(status_code=500, detail='Could not retrieve pypi statistics')


@app.middleware('http')
async def set_auth_header(request: Request, call_next, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Set authentication for further requests with siibra
    If a user provides a header, this one will be used otherwise use the default public token
    :param request: current request
    :param call_next: next middleware function
    :return: an altered response
    """
    auth = Authentication.instance()
    bearer_token = request.headers.get('Authorization')
    if bearer_token:
        auth.set_token(bearer_token.replace('Bearer ', ''))
    else:
        public_token=get_public_token()
        auth.set_token(public_token)
    response = await call_next(request)
    return response


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
            print('******* Im on production ********')
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
                except:
                    print('Could not log to matomo instance')
        else:
            print('Request for: {}'.format(request.url))
    response = await call_next(request)
    return response
