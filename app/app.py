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
from fastapi import FastAPI


import os

from fastapi import Request
from fastapi.templating import Jinja2Templates

import brainscapes_api

app = FastAPI()

app.include_router(brainscapes_api.router)

templates = Jinja2Templates(directory='templates/')


# Create a URL route in our application for "/"
@app.get('/')
def home(request: Request):
    # return render_template('index.html')
    return templates.TemplateResponse('index.html', context={'request': request})


async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response


@app.middleware("http")
async def matomo_request_log(request: Request, call_next):
    test_url = request.url
    headers = request.headers.get
    test_list = ['.css', '.js', '.png', '.gif', '.json', '.ico']
    res = any(ele in test_url for ele in test_list)

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
                    r = requests.get('https://stats.humanbrainproject.eu/matomo.php', params=payload)
                    print('Matomo logging with status: {}'.format(r.status_code))
                except:
                    print('Could not log to matomo instance')
        else:
            print('Request for: {}'.format(request.url))
    response = await call_next(request)
    return response


# If we're running in stand alone mode, run the application
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True)
