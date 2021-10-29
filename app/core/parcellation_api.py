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

import siibra
from enum import Enum
from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException
from siibra.core import Parcellation, Atlas, EbrainsDataset, Region, Space
from siibra.core.json_encoder import JSONEncoder
from fastapi.encoders import jsonable_encoder
from app.service.request_utils import get_base_url_from_request
from app.service.request_utils import get_global_features
from app.configuration.diskcache import memoize
from app.service.validation import validate_and_return_atlas, validate_and_return_parcellation
from app import logger

router = APIRouter()


class ModalityType(str, Enum):
    """
    A class for modality type, to provide selection options to swagger
    """
    ReceptorDistribution = 'ReceptorDistribution'
    GeneExpression = 'GeneExpression'
    ConnectivityProfile = 'ConnectivityProfile'
    ConnectivityMatrix = 'ConnectivityMatrix'



@router.get('/{atlas_id:path}/parcellations',
    tags=['parcellations'],
    response_model=List[Parcellation.typed_json_output])
def get_all_parcellations(atlas_id: str):
    """
    # Get all parcellations for an atlas

    Returns all parcellations that are defined in the siibra client for given atlas.

    ## code sample

    ```python
    import siibra

    atlas = siibra.atlases[f'{atlas_id}']
    parcellations = atlas.parcellations
    ```
    """
    try:
        atlas:Atlas = siibra.atlases[atlas_id]
        return [ JSONEncoder.encode(parc, nested=True) for parc in atlas.parcellations]
    except IndexError:
        raise HTTPException(400, detail=f'atlas with id {atlas_id} not found.')
    except Exception as e:
        logger.error('Error:', str(e))
        raise HTTPException(500, detail=f'something went wrong.')


@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/regions',
    tags=['parcellations'],
    response_model=List[Region.typed_json_output])
@memoize(typed=True)
def get_all_regions_for_parcellation_id(
        atlas_id: str,
        parcellation_id: str,
        space_id: Optional[str] = None):
    """
    # Get all regions of a parcellation

    Returns all regions for a given parcellation id. If space_id is present, only show regions that supports 

    ## code sample

    ```python
    import siibra
    from siibra.core import Parcellation, Atlas, Region

    atlas: Atlas = siibra.atlases[f'{atlas_id}']
    parcellation: Parcellation = atlas.parcellations[f'{parcellation_id}']
    regions: Region = parcellation.regiontree
    ```
    """
    try:
        atlas:Atlas = siibra.atlases[atlas_id]
        parcellation:Parcellation = atlas.parcellations[parcellation_id]
        space:Space = atlas.spaces[space_id] if space_id is not None else None
        parc = JSONEncoder.encode(parcellation, space=space, nested=True, detail=True)
        return parc.get('regions')
    except IndexError:
        raise HTTPException(400, detail=f'atlas with id {atlas_id} and/or parcellation with id {parcellation_id} not found.')
    except Exception as e:
        logger.error('Error:', str(e))
        raise HTTPException(500, detail=f'something went wrong.')



@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/features/{modality}/{modality_instance_name}',
            tags=['parcellations'])
def get_single_global_feature_detail(
        atlas_id: str,
        parcellation_id: str,
        modality: str,
        modality_instance_name: str,
        request: Request):
    """
    Returns a global feature for a specific modality id.
    """
    try:
        fs = get_global_features(atlas_id, parcellation_id, modality)
        found = [f for f in fs if f['src_name'] == modality_instance_name]
        if len(found) == 0:
            raise HTTPException(
                status_code=404,
                detail=f'modality with name {modality_instance_name} not found')

        return {
            'result': found[0]
        }
    except NotImplementedError:
        return HTTPException(status_code=501,
                             detail=f'modality {modality} not yet implemented')


@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/features/{modality}',
            tags=['parcellations'])
def get_single_global_feature(
        atlas_id: str,
        parcellation_id: str,
        modality: str,
        request: Request):
    """
    Returns a global feature for a parcellation, filtered by given modality.
    """
    try:
        fs = get_global_features(atlas_id, parcellation_id, modality)
        return [{
            'src_name': f['src_name'],
            'src_info': f['src_info'],
        } for f in fs]
    except NotImplementedError:
        return HTTPException(status_code=501,
                             detail=f'modality {modality} not yet implemented')


@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/features',
            tags=['parcellations'])
def get_global_features_rest(
        atlas_id: str,
        parcellation_id: str,
        request: Request):
    """
    # Get all types of global features

    Returns all available types of global features for a parcellation.
    """
    validate_and_return_atlas(atlas_id)
    validate_and_return_parcellation(parcellation_id)
    result = {
        'features': [
            {
                m.modality(): '{}atlases/{}/parcellations/{}/features/{}'.format(
                    get_base_url_from_request(request),
                    atlas_id.replace(
                        '/',
                        '%2F'),
                    parcellation_id.replace(
                        '/',
                        '%2F'),
                    m.modality()
                )} for m in siibra.features.modalities  # TODO siibra.get_features(parcellation, 'all') - too slow at the moment
        ]}

    return jsonable_encoder(result)


@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}',
            tags=['parcellations'],
            response_model=Parcellation.typed_json_output)
def get_parcellation_by_id(
        atlas_id: str,
        parcellation_id: str):
    """
    # Returns a specific parcellation

    Returns one parcellation by the specified parcellation_id and atlas_id.

    ## code sample

    ```python
    import siibra

    atlas = siibra.atlases[f'{atlas_id}']
    parcellation = atlas.parcellations[f'{parcellation_id}']
    ```
    """
    try:
        atlas:Atlas = siibra.atlases[atlas_id]
        parcellation:Parcellation = atlas.parcellations[parcellation_id]
        return JSONEncoder.encode(parcellation, nested=True, detail=False)
    except IndexError:
        raise HTTPException(400, detail=f'atlas with id {atlas_id} and/or parcellation with id {parcellation_id} not found.')
    except Exception as e:
        logger.error('Error:', str(e))
        raise HTTPException(500, detail=f'something went wrong.')

