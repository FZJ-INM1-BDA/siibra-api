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

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import PlainTextResponse
from fastapi.encoders import jsonable_encoder
from .atlas_api import ATLAS_PATH

from .request_utils import split_id, create_atlas

router = APIRouter()

# secure endpoints with the need to provide a bearer token
security = HTTPBearer()

# region === parcellations


def __parcellation_result_info(parcellation, atlas_id=None, request=None):
    """
    Parameters:
        - parcellation

    Create the response for a parcellation object
    """
    result_info = {
        "id": split_id(parcellation.id),
        "name": parcellation.name,
        }

    if request:
        result_info['links'] = {
                'parcellations': {
                    'href': '{}atlases/{}/parcellations/{}'.format(request.base_url, atlas_id.replace('/', '%2F'), parcellation.id.replace('/', '%2F'))
                }
        }
    if hasattr(parcellation, 'version') and parcellation.version:
        result_info['version'] = parcellation.version
    return result_info


@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations')
def get_all_parcellations(atlas_id: str, request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Parameters:
        - atlas_id

    Returns all parcellations that are defined in the brainscapes client for given atlas
    """
    if request.headers['accept'] == 'application/text':
        python_code = 'from brainscapes.atlas import REGISTRY \n ' \
                      'atlas = REGISTRY.MULTILEVEL_HUMAN_ATLAS \n ' \
                      'parcellations = atlas.parcellations'
        return PlainTextResponse(status_code=200, content=python_code)
    atlas = create_atlas(atlas_id)
    parcellations = atlas.parcellations
    result = []
    for parcellation in parcellations:
        result.append(__parcellation_result_info(parcellation, atlas_id, request))
    return jsonable_encoder(result)


@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}')
def get_parcellation_by_id(atlas_id: str, parcellation_id: str):
    """
    Parameters:
        - atlas_id
        - parcellation_id

    Returns one parcellation for given id or 404 Error if no parcellation is found.
    """
    atlas = create_atlas(atlas_id)
    parcellations = atlas.parcellations
    result = {}
    for parcellation in parcellations:
        if parcellation.id.find(parcellation_id):
            result = __parcellation_result_info(parcellation)
    if result:
        return jsonable_encoder(result)
    else:
        raise HTTPException(status_code=404, detail='parcellation with id: {} not found'.format(parcellation_id))


# endregion
