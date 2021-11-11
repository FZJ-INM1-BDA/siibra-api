from enum import Enum
import hashlib
from typing import List, Optional, Union
from siibra.core.jsonable import SiibraSerializable
from siibra.features.connectivity import ConnectivityProfile
from siibra.features.ebrains import EbrainsRegionalDataset
from siibra.features.receptors import ReceptorDistribution

from starlette.responses import FileResponse
from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

import siibra
from siibra.core import Atlas, Parcellation, Space, Region
from siibra.core.json_encoder import JSONEncoder
from siibra.features.feature import RegionalFeature

from app.service.validation import file_response_openapi
from app.service.request_utils import get_cached_file_path, fix_nii_for_neuroglancer
from app.configuration.diskcache import memoize

from app import logger


router = APIRouter(
    prefix='/regions'
)


# Required for correct typing
class ReceptorDistributionSchema(ReceptorDistribution.SiibraSerializationSchema): pass
class EbrainsDatasetSchema(EbrainsRegionalDataset.SiibraSerializationSchema): pass
ConnectivitySchema = ConnectivityProfile.SiibraSerializationSchema
RegionalFeatureModel = Union[
    ReceptorDistributionSchema,
    EbrainsDatasetSchema,
    ConnectivitySchema,
]


RegionalFeatureEnum = Enum('RegionalFeatureEnum', {
    mod.modality(): mod.modality() for mod in siibra.features.modalities
        if issubclass(mod._FEATURETYPE, RegionalFeature)
        and issubclass(mod._FEATURETYPE, SiibraSerializable)
})


class RegionalFeatureName(BaseModel):
    name: RegionalFeatureEnum


@router.get('/{region_id:path}/features',
            tags=['regions', 'features'],
            response_model=List[RegionalFeatureName])
def get_all_features_for_region(
        atlas_id: str,
        parcellation_id: str,
        region_id: str):
    """
    # Get all types of regional features

    Returns all available types of regional features.

    ## code sample
    python:get_all_feature_names_for_a_region.py
    """
    try:
        atlas: Atlas = siibra.atlases[atlas_id]
        parcellation: Parcellation = atlas.parcellations[parcellation_id]
        region: Region = parcellation.find_regions(region_id)[0]
        
        return [{
            'name': mod.value
        } for mod in RegionalFeatureEnum]
    except IndexError as e:
        raise HTTPException(401, detail=f'IndexError: {str(e)}')
    except Exception as e:
        raise HTTPException(500, detail=f'Uh oh, something went wrong. {str(e)}')


@router.get('/{region_id:path}/features/{modality_id}/{feature_id:path}',
    tags=['regions', 'features'],
    response_model=RegionalFeatureModel)
@memoize(typed=True)
def get_regional_modality_by_id(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        modality_id: RegionalFeatureEnum,
        feature_id: str,
        gene: Optional[str] = None):
    """
    # Get details of a regional features of a specific feature_id

    Returns details of a regional feature specified by the feature_id and the modality_id.


    ## code sample

    ```python
    import siibra
    from siibra.core import Atlas, Parcellation, Region

    atlas: Atlas = siibra.atlases[f'{atlas_id}']
    parcellation: Parcellation = atlas.parcellations[f'{parcellation_id}']
    region: Region = parcellation.find_regions(f'{region_id}')[0]
    features = siibra.get_features(region, f'{modality_id}')
    feature = [f for f in features if f.id == feature_id][0]
    ```
    """
    try:
        modality_id = modality_id.name
        atlas: Atlas = siibra.atlases[f'{atlas_id}']
        parcellation: Parcellation = atlas.parcellations[f'{parcellation_id}']
        region: Region = parcellation.find_regions(f'{region_id}')[0]
        
        if siibra.features.modalities[f'{modality_id}'] not in [mod for mod in siibra.features.modalities if issubclass(mod._FEATURETYPE, RegionalFeature) ]:
            raise HTTPException(404, detail=f'modality_id {modality_id} not a regional modality')
        
        features = siibra.get_features(region, f'{modality_id}')
        feature = [f for f in features if f.id == feature_id][0]
        return JSONEncoder.encode(feature, nested=True, detail=True)
    except IndexError as e:
        raise HTTPException(404, detail=f'IndexError: {str(e)}')


@router.get('/{region_id:path}/features/{modality_id}',
            tags=['regions', 'features'],
            response_model=List[RegionalFeatureModel])
@memoize(typed=True)
def get_feature_modality_for_region(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        modality_id: RegionalFeatureEnum,
        gene: Optional[str] = None):
    """
    # Get all regional features of a specific type

    Returns a list of all regional features of specified by the modality_id.


    ## code sample

    ```python
    import siibra
    from siibra.core import Atlas, Parcellation, Region

    atlas: Atlas = siibra.atlases[f'{atlas_id}']
    parcellation: Parcellation = atlas.parcellations[f'{parcellation_id}']
    region: Region = parcellation.find_regions(f'{region_id}')[0]
    features = siibra.get_features(region, f'{modality_id}')
    ```
    """

    try:
        modality_id = modality_id.name
        atlas: Atlas = siibra.atlases[f'{atlas_id}']
        parcellation: Parcellation = atlas.parcellations[f'{parcellation_id}']
        region: Region = parcellation.find_regions(f'{region_id}')[0]
        
        if siibra.features.modalities[f'{modality_id}'] not in [mod for mod in siibra.features.modalities if issubclass(mod._FEATURETYPE, RegionalFeature) ]:
            raise HTTPException(404, detail=f'modality_id {modality_id} not a regional modality')
        
        features = siibra.get_features(region, f'{modality_id}')
        return JSONEncoder.encode(features, nested=True, detail=False)
    except IndexError as e:
        raise HTTPException(404, detail=f'IndexError: {str(e)}')


class MinMaxModel(BaseModel):
    min: float
    max: float


@router.get('/{region_id:path}/regional_map/info',
            tags=['regions'],
            response_model=MinMaxModel)
@memoize(typed=True)
def get_regional_map_info(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        space_id: Optional[str] = None):
    """
    Returns information about a regional map for given region name.
    """
    atlas: Atlas = siibra.atlases[f'{atlas_id}']
    parcellation: Parcellation = atlas.parcellations[f'{parcellation_id}']
    space: Space = atlas.spaces[f'{space_id}']
    region: Region = parcellation.find_regions(f'{region_id}')[0]

    query_id = f'{atlas_id}{parcellation_id}{region.name}{space_id}'
    cached_filename = str(hashlib.sha256(query_id.encode('utf-8')).hexdigest()) + '.nii.gz'

    import nibabel as nib
    import numpy as np
    def get_nii_and_save(full_path):
        regional_map = region.get_regional_map(space, siibra.commons.MapType.CONTINUOUS)
        ng_fixed_nii = fix_nii_for_neuroglancer(regional_map.image)
        nib.save(ng_fixed_nii, full_path)
    cached_fullpath = get_cached_file_path(cached_filename, get_nii_and_save)
        
    nii = nib.load(cached_fullpath)
    return {
        'min': np.min(nii.dataobj),
        'max': np.max(nii.dataobj),
    }


@router.get('/{region_id:path}/regional_map/map',
            tags=['regions'],
            responses=file_response_openapi)
@memoize(typed=True)
def get_regional_map_file(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        space_id: Optional[str] = None):
    """
    # Get the probalistic map of the region of interest

    Get the probalistic map of the region of interest as a NiFTi .nii.gz file.

    ## code sample
    python:get_a_specific_map_of_one_region.py
    """
    try:
        atlas: Atlas = siibra.atlases[f'{atlas_id}']
        parcellation: Parcellation = atlas.parcellations[f'{parcellation_id}']
        space: Space = atlas.spaces[f'{space_id}']
        region: Region = parcellation.find_regions(f'{region_id}')[0]

        query_id = f'{atlas_id}{parcellation_id}{region.name}{space_id}'
        cached_filename = str(hashlib.sha256(query_id.encode('utf-8')).hexdigest()) + '.nii.gz'
        def get_nii_and_save(full_path):
            import nibabel as nib
            regional_map = region.get_regional_map(space, siibra.commons.MapType.CONTINUOUS)
            ng_fixed_nii = fix_nii_for_neuroglancer(regional_map.image)
            nib.save(ng_fixed_nii, full_path)
        cached_fullpath = get_cached_file_path(cached_filename, get_nii_and_save)
        
        return FileResponse(cached_fullpath, media_type='application/octet-stream')
    except IndexError as e:
        raise HTTPException(404, detail=f'IndexError: {str(e)}')


@router.get('/{region_id:path}',
            tags=['regions'],
            response_model=Region.SiibraSerializationSchema)
def get_region_by_name_api(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        space_id: Optional[str] = None):
    """
    # Returns a specific region

    Returns a region specific by the region_id, parcellation_id and atlas_id. 
    If space_id is present as query param, space specific data will also be fetched.

    ## code sample
    python:get_one_region_with_further_details_for_one_parcellation.py
    """
    try:
        atlas:Atlas = siibra.atlases[atlas_id]
        parcellation:Parcellation = atlas.parcellations[parcellation_id]
        region: Region = parcellation.find_regions(region_id)[0]
        space: Space = atlas.spaces[space_id] if space_id is not None else None
        # polyfill for https://github.com/FZJ-INM1-BDA/siibra-python/issues/98
        if space == siibra.spaces['fsaverage']:
            space = None
        return JSONEncoder.encode(region, nested=True, space=space, detail=True)
    except IndexError as e:
        raise HTTPException(404, detail=f'Index Error: {str(e)}')
    except Exception as e:
        logger.error('Error:', str(e))
        raise HTTPException(500, detail=f'Error. {str(e)}')
