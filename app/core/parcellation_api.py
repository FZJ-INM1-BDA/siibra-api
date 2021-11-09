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

from enum import Enum
from pydantic import BaseModel
import siibra
from typing import List, Optional
from fastapi import APIRouter, HTTPException

from siibra.core import Parcellation, Atlas, Region, Space
from siibra.core.json_encoder import JSONEncoder
from siibra.features.connectivity import ConnectivityMatrix
from siibra.features.feature import ParcellationFeature
from siibra.core.jsonable import SiibraSerializable

from app.configuration.diskcache import memoize
from app import logger
from .region_api import router as region_router

router = APIRouter(
    prefix='/parcellations'
)


ParcellationFeatureEnum: Enum = Enum('ParcellationFeatureEnum', {
    mod.modality(): mod.modality() for mod in siibra.features.modalities
        if issubclass(mod._FEATURETYPE, ParcellationFeature)
        and issubclass(mod._FEATURETYPE, SiibraSerializable)
})


router.include_router(region_router, prefix='/{parcellation_id:path}')


@router.get('',
            tags=['parcellations'],
            response_model=List[Parcellation.SiibraSerializationSchema])
@memoize(typed=True)
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
        raise HTTPException(404, detail=f'atlas with id {atlas_id} not found.')
    except Exception as e:
        logger.error('Error:', str(e))
        raise HTTPException(500, detail=f'something went wrong.')


@router.get('/{parcellation_id:path}/regions',
            tags=['parcellations', 'regions'],
            response_model=List[Region.SiibraSerializationSchema])
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
        # polyfill for https://github.com/FZJ-INM1-BDA/siibra-python/issues/98
        if space == siibra.spaces['fsaverage']:
            space = None
        parc = JSONEncoder.encode(parcellation, space=space, include_regions=True, nested=True, detail=True)
        return parc.get('regions')
    except IndexError as e:
        print('uhoh', e, atlas_id, parcellation_id)
        raise HTTPException(404, detail=f'atlas with id {atlas_id} and/or parcellation with id {parcellation_id} not found.')
    except Exception as e:
        logger.error('Error:', str(e))
        raise HTTPException(500, detail=f'something went wrong.')



@router.get('/{parcellation_id:path}/features/{modality_id}/{feature_id}',
            tags=['parcellations', 'features'],
            response_model=ConnectivityMatrix.SiibraSerializationSchema)
@memoize(typed=True)
def get_single_global_feature_detail(
        atlas_id: str,
        parcellation_id: str,
        modality_id: ParcellationFeatureEnum,
        feature_id: str):
    """
    # Get detail of a parcellation feature by feature_id

    Returns detailed information of a specific parcellation feature identified by feature_id.

    ## code sample
    ```python

    import siibra
    from siibra.core import Atlas, Parcellation

    atlas: Atlas = siibra.atlases[f'{atlas_id}']
    parcellation: Parcellation = atlas.parcellations[f'{parcellation_id}']
    specific_feature, = [f for f in siibra.get_features(parcellation, f'{modality_id}') if f.id == f'{feature_id}']
    ```
    """
    try:
        atlas: Atlas = siibra.atlases[atlas_id]
        parcellation: Parcellation = atlas.parcellations[parcellation_id]
        if siibra.features.modalities[modality_id].modality() not in [mod.value for mod in modality_id ]:
            raise HTTPException(404, detail=f'modality_id {modality_id} not a parcellation modality_id')

        filtered_features = [f for f in siibra.get_features(parcellation, modality_id) if f.id == feature_id]
        if not filtered_features:
            raise HTTPException(404, detail=f'feature with id {feature_id} not found.')

        return JSONEncoder.encode(filtered_features[0], nested=True, detail=True)
    except IndexError as e:
        raise HTTPException(404, detail=f'IndexError: {str(e)}')


@router.get('/{parcellation_id:path}/features/{modality_id}',
            tags=['parcellations', 'features'],
            response_model=List[ConnectivityMatrix.SiibraSerializationSchema])
@memoize(typed=True)
def get_single_global_feature(
        atlas_id: str,
        parcellation_id: str,
        modality_id: ParcellationFeatureEnum):
    """
    # Get all parcellation features of a specific type

    Returns a list of parcellation features specified by modality_id.


    ## code sample

    ```python
    import siibra
    from siibra.core import Atlas, Parcellation

    atlas: Atlas = siibra.atlases[f'{atlas_id}']
    parcellation: Parcellation = atlas.parcellations[f'{parcellation_id}']
    siibra.get_features(parcellation, f'{modality_id}')
    ```
    """

    try:
        atlas: Atlas = siibra.atlases[atlas_id]
        parcellation: Parcellation = atlas.parcellations[parcellation_id]
        if siibra.features.modalities[modality_id].modality() not in [enum.value for enum in ParcellationFeatureEnum]:
            raise HTTPException(404, detail=f'modality_id {modality_id} not a parcellation modality')

        return JSONEncoder.encode(siibra.get_features(parcellation, modality_id), nested=True, detail=False)
    except IndexError as e:
        raise HTTPException(404, detail=f'IndexError: {str(e)}')
    

class NamedModel(BaseModel):
    name: ParcellationFeatureEnum

@router.get('/{parcellation_id:path}/features',
            tags=['parcellations', 'features'],
            response_model=List[NamedModel])
@memoize(typed=True)
def get_global_feature_names(
        atlas_id: str,
        parcellation_id: str):
    """
    # Get all types of global features

    Returns all available types of parcellation features for a parcellation.

    ## code sample

    ```python
    import siibra
    from siibra.features.feature import ParcellationFeature

    parcellation_feature_types = [mod for mod in siibra.features.modalities if issubclass(mod._FEATURETYPE, ParcellationFeature) ]
    ```
    """
    
    try:
        # only required for validation
        _atlas:Atlas = siibra.atlases[atlas_id]
        _parcellation:Parcellation = _atlas.parcellations[parcellation_id]
        return [{
            'name': mod.value
        } for mod in ParcellationFeatureEnum ]
    except IndexError as e:
        raise HTTPException(404, detail=f'IndexError: {str(e)}')


@router.get('/{parcellation_id:path}',
            tags=['parcellations'],
            response_model=Parcellation.SiibraSerializationSchema)
@memoize(typed=True)
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
        return JSONEncoder.encode(parcellation, nested=True, detail=True)
    except IndexError:
        raise HTTPException(404, detail=f'atlas with id {atlas_id} and/or parcellation with id {parcellation_id} not found.')
    except Exception as e:
        logger.error('Error:', str(e))
        raise HTTPException(500, detail=f'something went wrong.')

