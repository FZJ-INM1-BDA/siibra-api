from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from siibra.retrieval.requests import HttpRequest
from starlette.responses import FileResponse
from app.service.validation import validate_and_return_atlas, validate_and_return_parcellation, \
    validate_and_return_space, validate_and_return_region
from app.service.request_utils import get_base_url_from_request, get_path_to_regional_map, get_regional_feature, siibra_custom_json_encoder
from app.configuration.diskcache import memoize

import siibra
from siibra.core import Atlas, Parcellation, Space, Region
from siibra.core.json_encoder import JSONEncoder
from app import logger

router = APIRouter()

@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features',
            tags=['regions'])
def get_all_features_for_region(
        request: Request,
        atlas_id: str,
        parcellation_id: str,
        region_id: str):
    """
    Returns all regional features for a region.
    """
    try:
        atlas: Atlas = siibra.atlases[atlas_id]
        parcellation: Parcellation = atlas.parcellations[parcellation_id]
        region: Region = parcellation.decode_region(region_id)

        return {
        'features': [
            {
                feature_name: '{}atlases/{}/parcellations/{}/regions/{}/features/{}'.format(
                    get_base_url_from_request(request),
                    atlas_id.replace(
                        '/',
                        '%2F'),
                    parcellation_id.replace(
                        '/',
                        '%2F'),
                    region_id.replace(
                        '/',
                        '%2F'),
                    feature_name
                )
            } for feature_name in siibra.get_features(region, 'all')]}
    except IndexError as e:
        raise HTTPException(401, detail=f'IndexError: {str(e)}')
    except Exception as e:
        raise HttpRequest(500, detail=f'Uh oh, something went wrong. {str(e)}')



# TODO - can maybe be removed
# negative: need to be able to fetch region specific feature. XG
@router.get(
    '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features/{modality}/{feature_id:path}',
    tags=['regions'])
@memoize(typed=True)
def get_regional_modality_by_id(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        modality: str,
        feature_id: str,
        gene: Optional[str] = None):
    """
    Returns a feature for a region, as defined by by the modality and feature ID
    """
    regional_features = get_regional_feature(
        atlas_id, parcellation_id, region_id, modality, feature_id=feature_id, detail=True, gene=gene)
    if len(regional_features) == 0:
        raise HTTPException(
            status_code=404,
            detail=f'modality with id {feature_id} not found')
    if len(regional_features) != 1:
        raise HTTPException(
            status_code=400,
            detail=f'modality with id {feature_id} has multiple matches')
    return jsonable_encoder(regional_features[0],
        custom_encoder=siibra_custom_json_encoder)


# TODO - can maybe be removed
# negative: need to be able to fetch region specific feature. XG
@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features/{modality}',
            tags=['regions'])
@memoize(typed=True)
def get_feature_modality_for_region(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        modality: str,
        gene: Optional[str] = None):
    """
    Returns list of the features for a region, as defined by the modality.
    """
    regional_features = get_regional_feature(
        atlas_id, parcellation_id, region_id, modality, detail=False, gene=gene)

    return regional_features


def parse_region_selection(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        space_id: str):
    if space_id is None:
        raise HTTPException(
            status_code=400,
            detail='space_id is required for this functionality')

    space_of_interest = validate_and_return_space(space_id)
    validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id)
    region = validate_and_return_region(region_id, parcellation)
    if region is None:
        raise HTTPException(
            status_code=404,
            detail=f'cannot find region with spec {region_id}')
    # if len(region) > 1:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f'found multiple region withs pec {region_id}')
    return region, space_of_interest


@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/regional_map/info',
            tags=['regions'])
@memoize(typed=True)
def get_regional_map_info(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        space_id: Optional[str] = None):
    """
    Returns information about a regional map for given region name.
    """
    validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id)
    region = validate_and_return_region(region_id, parcellation)
    region.get_regional_map("mni152", siibra.MapType.CONTINUOUS)

    roi, space_of_interest = parse_region_selection(
        atlas_id, parcellation_id, region_id, space_id)
    query_id = f'{atlas_id}{parcellation_id}{roi.name}{space_id}'
    cached_fullpath = get_path_to_regional_map(
        query_id, roi, space_of_interest)
    import nibabel as nib
    import numpy as np
    nii = nib.load(cached_fullpath)
    data = nii.get_fdata()
    return {
        'min': np.min(data),
        'max': np.max(data),
    }


@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/regional_map/map',
            tags=['regions'])
@memoize(typed=True)
def get_regional_map_file(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        space_id: Optional[str] = None):
    """
    Returns a regional map for given region name.
    """
    roi, space_of_interest = parse_region_selection(
        atlas_id, parcellation_id, region_id, space_id)
    query_id = f'{atlas_id}{parcellation_id}{roi.name}{space_id}'
    cached_fullpath = get_path_to_regional_map(
        query_id, roi, space_of_interest)
    return FileResponse(cached_fullpath, media_type='application/octet-stream')


@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}',
            tags=['regions'],
            response_model=Region.typed_json_output)
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

    ```python
    import siibra
    from siibra.core import Parcellation, Atlas

    atlas: Atlas = siibra.atlases[f'{atlas_id}']
    parcellation: Parcellation = atlas.parcellations[f'{parcellation_id}']
    region = parcellation.decode_region(f'{region_id}')
    ```
    """
    try:
        atlas:Atlas = siibra.atlases[atlas_id]
        parcellation:Parcellation = atlas.parcellations[parcellation_id]
        region: Region = parcellation.decode_region(region_id)
        space: Space = atlas.spaces[space_id] if space_id is not None else None
        return JSONEncoder.encode(region, nested=True, space=space, detail=True)
    except IndexError as e:
        raise HTTPException(400, detail=f'Index Error: {str(e)}')
    except Exception as e:
        logger.error('Error:', str(e))
        raise HTTPException(500, detail=f'Error. {str(e)}')
