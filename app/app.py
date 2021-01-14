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
from brainscapes.authentication import Authentication
from fastapi import FastAPI, Depends

import os

from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates

import brainscapes_api

security = HTTPBearer()

# Main fastAPI application
app = FastAPI()
# Add a brainscapes router with further endpoints
app.include_router(brainscapes_api.router)
# Template list, with every template in the project
# can be rendered and returned
templates = Jinja2Templates(directory='templates/')


@app.get('/')
def home(request: Request):
    """
    Return the template for the brainscapes landing page.

    :param request: fastApi Request object
    :return: the rendered index.html template
    """
    return templates.TemplateResponse('index.html', context={'request': request})


@app.middleware("http")
async def set_auth_header(request: Request, call_next, credentials: HTTPAuthorizationCredentials = Depends(security)):
    auth = Authentication.instance()
    bearer_token = request.headers.get("Authorization")
    if bearer_token:
        auth.set_token(bearer_token.replace("Bearer ", ""))
    response = await call_next(request)
    return response


@app.middleware("http")
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

    if 'BRAINSCAPES_ENVIRONMENT' in os.environ:
        if os.environ['BRAINSCAPES_ENVIRONMENT'] == 'PRODUCTION':
            print('******* Im on production ********')
            if not res:
                payload = {
                        'idsite': 13,
                        'rec': 1,
                        'action_name': 'brainscapes_api',
                        'url': request.url,
                        '_id': 'my_ip',
                        'lang':  request.headers.get('Accept-Language'),
                        'ua': request.headers.get('User-Agent')
                }
                try:
                    # r = requests.get('https://stats.humanbrainproject.eu/matomo.php', params=payload)
                    print('Matomo logging with status: {}'.format(r.status_code))
                except:
                    print('Could not log to matomo instance')
        else:
            print('Request for: {}'.format(request.url))
    response = await call_next(request)
    return response
