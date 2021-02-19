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
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import PlainTextResponse
from fastapi.encoders import jsonable_encoder
from .atlas_api import ATLAS_PATH
from .request_utils import split_id, create_atlas, create_region_json_object, _add_children_to_region, find_space_by_id
from brainscapes.features import regionprops


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


@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions')
def get_all_regions_for_parcellation_id(atlas_id: str, parcellation_id: str):
    """
    Parameters:
        - atlas_id
        - parcellation_id

    Returns all regions for a given parcellation id.
    """
    # select atlas by id
    atlas = create_atlas(atlas_id)
    try:
        # select atlas parcellation
        atlas.select_parcellation(parcellation_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail='The requested parcellation is not supported by the selected atlas.'
        )

    result = []
    for region in atlas.regiontree.children:
        region_json = create_region_json_object(region)
        _add_children_to_region(region_json, region)
        result.append(region_json)
    return result


@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}')
def get_region_by_name(atlas_id: str, parcellation_id: str, region_id: str, space_id: Optional[str] = None):
    """
    Parameters:
        - atlas_id
        - space_id
        - region_id

    Returns all regions for a given space id.
    """
    # select atlas by id
    atlas = create_atlas(atlas_id)
    # select atlas parcellation
    atlas.select_parcellation(parcellation_id)
    region = atlas.regiontree.find(region_id)

    r = region[0]
    region_json = create_region_json_object(r)
    _add_children_to_region(region_json, r)

    if space_id:
        atlas.select_region(r)
        r_props = regionprops.RegionProps(atlas, find_space_by_id(atlas, space_id))
        region_json['props'] = {}
        region_json['props']['centroid_mm'] = list(r_props.attrs['centroid_mm'])
        region_json['props']['volume_mm'] = r_props.attrs['volume_mm']
        region_json['props']['surface_mm'] = r_props.attrs['surface_mm']
        region_json['props']['is_cortical'] = r_props.attrs['is_cortical']

    return jsonable_encoder(region_json)


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
        if parcellation.id.find(parcellation_id) != -1:
            result = __parcellation_result_info(parcellation)
    if result:
        return jsonable_encoder(result)
    else:
        raise HTTPException(status_code=404, detail='parcellation with id: {} not found'.format(parcellation_id))


# endregion
