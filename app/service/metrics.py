# Copyright 2018-2022 Institute of Neuroscience and Medicine (INM-1),
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

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import psutil
import requests
import json
from app import logger
import siibra

router = APIRouter()
templates = Jinja2Templates(directory='templates/')
pypi_stat_url = 'https://pypistats.org/api/packages/siibra/overall?mirrors=false'


@router.get('/metrics', include_in_schema=False)
def get_metrics():
    return JSONResponse(
        status_code=200,
        content={
            'cpu': {
                'usage': f'{psutil.cpu_percent(4)} %',
                'count': psutil.cpu_count()
            },
            'memory': {
                'used': f'{psutil.virtual_memory().used >> 20} MB',
                'free': f'{psutil.virtual_memory().free >> 20} MB'
            },
            'disk': {
                'used': f'{psutil.disk_usage("/").used >> 20} MB',
                'free': f'{psutil.disk_usage("/").free >> 20} MB'
            },
            'siibra-python': {
                'version': siibra.__version__
            }
        }
    )


@router.get('/stats', include_in_schema=False)
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

