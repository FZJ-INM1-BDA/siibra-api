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

import re
import siibra
from enum import Enum
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.responses import PlainTextResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from .request_utils import split_id, find_region_via_id, create_region_json_response
from .request_utils import get_spaces_for_parcellation, get_base_url_from_request, siibra_custom_json_encoder
from .request_utils import get_global_features, get_regional_feature, get_path_to_regional_map, origin_data_decoder
from .request_utils import get_region_props
from .diskcache import fanout_cache
from .validation import validate_and_return_atlas, validate_and_return_parcellation, validate_and_return_space
from .ebrains_token import get_public_token
from . import logger

preheat_flag=False


def get_preheat_status():
    global preheat_flag
    return preheat_flag


def preheat(id=None):
    global preheat_flag
    logger.info('--start parcellation preheat--')
    #TODO - check if preheat is still needed
    # public_token = get_public_token()
    # siibra.set_ebrains_token(public_token)
    # # feature_class = siibra.modalities.keys()
    # # EbrainsRegionalFeatureCls=feature_classes[feature_modalities.EbrainsRegionalDataset]
    # EbrainsRegionalFeatureCls=feature_classes[feature_modalities.EbrainsRegionalDataset]
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

# TODO instead of selecting, maybe check for a valid parcellation
# def __check_and_select_parcellation(atlas, parcellation_id):
#     try:
#         # select atlas parcellation
#         atlas.select_parcellation(parcellation_id, force=True)
#     except Exception:
#         raise HTTPException(
#             status_code=400,
#             detail='The requested parcellation is not supported by the selected atlas.')


def __parcellation_result_info(parcellation, atlas_id=None, request=None):
    """
    Parameters:
        - parcellation

    Create the response for a parcellation object
    """
    result_info = {
        'id': split_id(parcellation.id),
        'name': parcellation.name,
        'availableSpaces': get_spaces_for_parcellation(parcellation),
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
        }
    }

    if hasattr(parcellation, 'modality') and parcellation.modality:
        result_info['modality'] = parcellation.modality

    if hasattr(parcellation, 'version') and parcellation.version:
        result_info['version'] = parcellation.version

    if hasattr(parcellation, 'volume_src') and parcellation.volume_src:
        volumeSrc = {
            key.id: value for key, value in parcellation.volume_src.items()
        }
        result_info['volumeSrc'] = jsonable_encoder(
            volumeSrc, custom_encoder=siibra_custom_json_encoder)
    if hasattr(parcellation, 'origin_datainfos'):
        original_infos=[]
        for datainfo in parcellation.origin_datainfos:
            try:
                original_info=origin_data_decoder(datainfo)
                original_infos.append(original_info)
            except RuntimeError:
                continue

        result_info['originDatainfos'] = original_infos

    if hasattr(parcellation, 'deprecated'):
        result_info['deprecated'] = parcellation.deprecated

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
@fanout_cache.memoize(typed=True)
def get_all_regions_for_parcellation_id(
        atlas_id: str,
        parcellation_id: str,
        space_id: Optional[str] = None):
    """
    Returns all regions for a given parcellation id.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id)

    result = []
    for region in parcellation.regiontree.children:
        region_json = create_region_json_response(region, space_id, atlas)
        result.append(region_json)
    return result


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
    # TODO check for valid atlas and parcellation
    atlas = validate_and_return_atlas(atlas_id)

    #TODO will be done in siibra-python
    #TODO Authentication error - Not working in the moment for the provided user
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
                    m)} for m in siibra.get_features(region_id, 'all')]}

    return jsonable_encoder(result)


# TODO - can maybe be removed
@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features/{modality}/{modality_id:path}',
            tags=['parcellations'])
def get_regional_modality_by_id(
        request: Request,
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        modality: str,
        modality_id: str,
        gene: Optional[str] = None):
    """
    Returns all features for a region. The returned feature is defined by the given modality type and modality id.
    """
    regional_features = get_regional_feature(
        atlas_id, parcellation_id, region_id, modality, feature_id=modality_id, detail=True, gene=gene)

    if len(regional_features) == 0:
        raise HTTPException(
            status_code=404,
            detail=f'modality with id {modality_id} not found')
    # if len(regional_features) != 1:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f'modality with id {modality_id} has multiple matches')
    # return regional_features[0]
    return regional_features


# TODO - can maybe be removed
@router.get('/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features/{modality}',
            tags=['parcellations'])
def get_feature_modality_for_region(
        request: Request,
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        modality: str,
        gene: Optional[str] = None):
    """
    Returns one modality feature for a region.
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
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = atlas.get_parcellation(parcellation_id)
    region = atlas.get_region(region_id, parcellation)
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
@fanout_cache.memoize(typed=True)
def get_regional_map_info(
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        space_id: Optional[str] = None):
    """
    Returns information about a regional map for given region name.
    """
    atlas = siibra.atlases[atlas_id]
    region = atlas.get_region(region_id, parcellation=parcellation_id)
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
@fanout_cache.memoize(typed=True)
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
def get_region_by_name(
        request: Request,
        atlas_id: str,
        parcellation_id: str,
        region_id: str,
        space_id: Optional[str] = None):
    """
    Returns a specific region for a given id.
    """
    atlas = siibra.atlases[atlas_id]
    parcellation = atlas.get_parcellation(parcellation_id)
    region = atlas.get_region(region_id, parcellation)

    #TODO New Region not found error

    # if len(region) == 0:
    #     raise HTTPException(status_code=404,
    #                         detail=f'region with spec {region_id} not found')
    # r = region[0]
    region_json = create_region_json_response(region, space_id, atlas, detail=True)
    if space_id:
        region_json['props'] = get_region_props(space_id, atlas, region)

    single_region_root_url = '{}atlases/{}/parcellations/{}/regions/{}'.format(
        get_base_url_from_request(request),
        atlas_id.replace('/', '%2F'),
        parcellation_id.replace('/', '%2F'),
        region_id.replace('/', '%2F'))

    region_json['links'] = {
        'features': f'{single_region_root_url}/features',
        'regional_map_info': f'{single_region_root_url}/regional_map/info?space_id={space_id}' if region_json['hasRegionalMap'] else None,
        'regional_map': f'{single_region_root_url}/regional_map/map?space_id={space_id}' if region_json['hasRegionalMap'] else None,
    }

    return jsonable_encoder(region_json)


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
    atlas = siibra.atlases[atlas_id]
    parcellation = atlas.get_parcellation(parcellation_id)
    result = {
        'features': [
            {
                m: '{}atlases/{}/parcellations/{}/features/{}'.format(
                    get_base_url_from_request(request),
                    atlas_id.replace(
                        '/',
                        '%2F'),
                    parcellation_id.replace(
                        '/',
                        '%2F'),
                    m)} for m in siibra.get_features(parcellation, 'all')]}

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
    atlas = siibra.atlases[atlas_id]
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
