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
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from starlette.responses import FileResponse
from fastapi.encoders import jsonable_encoder
from app.service.request_utils import get_region_by_name, region_encoder, split_id
from app.service.request_utils import get_spaces_for_parcellation, get_base_url_from_request, siibra_custom_json_encoder
from app.service.request_utils import get_global_features, get_regional_feature, get_path_to_regional_map
from app.configuration.diskcache import memoize
from app.service.validation import validate_and_return_atlas, validate_and_return_parcellation, \
    validate_and_return_space, validate_and_return_region
from app import logger

preheat_flag = False

parcellation_json_encoder = {
    siibra.core.Parcellation: lambda parcellation: {
        'id': split_id(parcellation.id),
        'name': parcellation.name,
        'availableSpaces': get_spaces_for_parcellation(parcellation),
        'modality': parcellation.modality,
        'version': parcellation.version,
        '_dataset_specs': parcellation._dataset_specs,
    }
}

def get_preheat_status():
    global preheat_flag
    return preheat_flag


def preheat(id=None):
    global preheat_flag
    logger.info('--start parcellation preheat--')
    # TODO - check if preheat is still needed
    # public_token = get_public_token()
    # siibra.set_ebrains_token(public_token)
    # # feature_class = siibra.modalities.keys()
    # # EbrainsRegionalFeatureCls=feature_classes[feature_modalities.EbrainsRegionalDataset]
    # EbrainsRegionalFeatureCls=feature_registry._classes[feature_modalities.EbrainsRegionalDataset]
    # if hasattr(EbrainsRegionalFeatureCls, 'preheat') and callable(EbrainsRegionalFeatureCls.preheat):
    #     EbrainsRegionalFeatureCls.preheat(id)
    #     logger.info('--end parcellation preheat--')
    # else:
    #     logger.info('--siibra-python does not suppport preheat. exiting--')
    # preheat_flag=True

router = APIRouter()


class ModalityType(str, Enum):
    """
    A class for modality type, to provide selection options to swagger
    """
    ReceptorDistribution = 'ReceptorDistribution'
    GeneExpression = 'GeneExpression'
    ConnectivityProfile = 'ConnectivityProfile'
    ConnectivityMatrix = 'ConnectivityMatrix'


# region === parcellations


def __parcellation_result_info(parcellation, atlas_id=None, request=None):
    """
    Parameters:
        - parcellation

    Create the response for a parcellation object
    """
    result_info = {
        'links': {
            'self': {
                'href': '{}atlases/{}/parcellations/{}'.format(get_base_url_from_request(request),
                                                               atlas_id.replace('/', '%2F'),
                                                               parcellation.id.replace('/', '%2F'))
            }
        },
        'regions': {
            'href': '{}atlases/{}/parcellations/{}/regions'.format(
                get_base_url_from_request(request),
                atlas_id.replace('/', '%2F'),
                parcellation.id.replace('/', '%2F')
            )
        },
        'features': {
            'href': '{}atlases/{}/parcellations/{}/features'.format(
                get_base_url_from_request(request),
                atlas_id.replace('/', '%2F'),
                parcellation.id.replace('/', '%2F')
            )
        },
        **jsonable_encoder(parcellation, custom_encoder={
            **siibra_custom_json_encoder,
            **parcellation_json_encoder
        })
    }

    return result_info


@router.get('/{atlas_id:path}/parcellations', tags=['parcellations'])
def get_all_parcellations(atlas_id: str, request: Request):
    """
    Returns all parcellations that are defined in the siibra client for given atlas.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellations = atlas.parcellations
    return [
        __parcellation_result_info(
            parcellation,
            atlas_id,
            request) for parcellation in parcellations]


@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/regions', tags=['parcellations'])
@memoize(typed=True)
def get_all_regions_for_parcellation_id(
        atlas_id: str,
        parcellation_id: str,
        space_id: Optional[str] = None):
    """
    Returns all regions for a given parcellation id.
    """
    parcellation = validate_and_return_parcellation(parcellation_id)
    space = validate_and_return_space(space_id)
    
    return [ region_encoder(region, space=space) for region in parcellation.regiontree.children ]


@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features',
            tags=['parcellations'])
def get_all_features_for_region(
        request: Request,
        atlas_id: str,
        parcellation_id: str,
        region_id: str):
    """
    Returns all regional features for a region.
    """
    validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id)
    region = validate_and_return_region(region_id, parcellation)

    result = {
        'features': [
            {
                m: '{}atlases/{}/parcellations/{}/regions/{}/features/{}'.format(
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
                    m)} for m in siibra.get_features(region, 'all')]}

    return jsonable_encoder(result)


# TODO - can maybe be removed
# negative: need to be able to fetch region specific feature. XG
@router.get(
    '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features/{modality}/{feature_id:path}',
    tags=['parcellations'])
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
            tags=['parcellations'])
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
            tags=['parcellations'])
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
            tags=['parcellations'])
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
    print(f'region: {roi}')
    print(f'space: {space_of_interest}')
    query_id = f'{atlas_id}{parcellation_id}{roi.name}{space_id}'
    print(f'queryId: {query_id}')
    cached_fullpath = get_path_to_regional_map(
        query_id, roi, space_of_interest)
    print(f'cached path: {cached_fullpath}')
    return FileResponse(cached_fullpath, media_type='application/octet-stream')


@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}',
            tags=['parcellations'])
def get_region_by_name_api(
        request: Request,
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        space_id: Optional[str] = None):
    """
    Returns a specific region for a given id.
    """
    base_url=get_base_url_from_request(request)
    return get_region_by_name(base_url, atlas_id, parcellation_id, region_id, space_id)


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
    Returns all global features for a parcellation.
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
            tags=['parcellations'])
def get_parcellation_by_id(
        atlas_id: str,
        parcellation_id: str,
        request: Request):
    """
    Returns one parcellation for given id.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellations = atlas.parcellations
    result = {}
    for parcellation in parcellations:
        if parcellation.id.find(parcellation_id) != -1:
            result = __parcellation_result_info(
                parcellation, atlas_id, request)
    if result:
        return jsonable_encoder(
            result, custom_encoder=siibra_custom_json_encoder)
    else:
        raise HTTPException(
            status_code=404,
            detail='parcellation with id: {} not found'.format(parcellation_id))

# endregion
