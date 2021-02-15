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

from fastapi import APIRouter, Request, HTTPException
from brainscapes.atlas import REGISTRY

# FastApi router to create rest endpoints
router = APIRouter()

# Base URL for all endpoints
ATLAS_PATH = '/atlases'


# region === atlases

@router.get('/atlases')
def get_all_atlases():
    """
    Get all atlases known by brainscapes
    """
    atlases = REGISTRY.items
    result = []
    for a in atlases:
        result.append({
            'id': a.id,#.replace('/', '-'),
            'name': a.name
        })
    return result


@router.get(ATLAS_PATH + '/{atlas_id:path}')
def get_atlas_by_id(atlas_id: str, request: Request):
    """
    Parameters:
        - atlas_id: Atlas id

    Get more information for a specific atlas with links to further objects.
    """
    atlases = REGISTRY.items
    for a in atlases:
        if a.id == atlas_id.replace('%2F', '/'):#.replace('-', '/'):
            return {
                'id': a.id,#.replace('/', '-'),
                'name': a.name,
                'links': {
                    'parcellations': {
                        'href': '{}atlases/{}/parcellations'.format(request.base_url, atlas_id.replace('/', '%2F'))
                    },
                    'spaces': {
                        'href': '{}atlases/{}/spaces'.format(request.base_url, atlas_id.replace('/', '%2F'))
                    }
                }
            }
    raise HTTPException(status_code=404, detail='atlas with id: {} not found'.format(atlas_id))
# endregion
