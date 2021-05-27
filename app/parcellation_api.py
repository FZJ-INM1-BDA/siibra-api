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
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.responses import PlainTextResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from .atlas_api import ATLAS_PATH
from .request_utils import split_id, create_atlas, create_region_json_object, create_region_json_object_tmp, \
    _add_children_to_region, find_space_by_id, find_region_via_id, get_global_features, get_regional_feature, get_cached_file
from .request_utils import get_spaces_for_parcellation, get_base_url_from_request
from siibra import spaces as siibra_spaces, region as siibra_region, commons as siibra_commons
from siibra.features import feature as feature_export,classes as feature_classes,modalities as feature_modalities
import re
from .diskcache import fanout_cache
import hashlib

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


def __check_and_select_parcellation(atlas, parcellation_id):
    try:
        # select atlas parcellation
        atlas.select_parcellation(parcellation_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail='The requested parcellation is not supported by the selected atlas.'
        )


def __parcellation_result_info(parcellation, atlas_id=None, request=None):
    """
    Parameters:
        - parcellation

    Create the response for a parcellation object
    """
    result_info = {
        'id': split_id(parcellation.id),
        'name': parcellation.name,
        'availableSpaces': get_spaces_for_parcellation(parcellation.name),
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
        volumeSrc={
            key.id: value for key, value in parcellation.volume_src.items()
        }
        result_info['volumeSrc']=volumeSrc
    
    return result_info


@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations')
def get_all_parcellations(atlas_id: str, request: Request):
    """
    Parameters:
        - atlas_id

    Returns all parcellations that are defined in the siibra client for given atlas
    """
    if request.headers['accept'] == 'application/text':
        python_code = 'from siibra.atlas import REGISTRY \n ' \
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
@fanout_cache.memoize(typed=True, expire=60*60)
def get_all_regions_for_parcellation_id(atlas_id: str, parcellation_id: str, space_id: Optional[str] = None):
    """
    Parameters:
        - atlas_id
        - parcellation_id

    Returns all regions for a given parcellation id.
    """
    # select atlas by id
    atlas = create_atlas(atlas_id)
    __check_and_select_parcellation(atlas, parcellation_id)

    result = []
    for region in atlas.selected_parcellation.regiontree.children:
        # region_json = create_region_json_object(region)
        region_json = create_region_json_object_tmp(region, space_id, atlas)
        # _add_children_to_region(region_json, region)
        result.append(region_json)
    return result


@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features')
def get_all_features_for_region(request: Request, atlas_id: str, parcellation_id: str, region_id: str):
    """
    Parameters:
        - atlas_id
        - parcellation_id
        - region_id

    Returns all regional features for a region.
    """
    # select atlas by id
    atlas = create_atlas(atlas_id)
    # select atlas parcellation
    __check_and_select_parcellation(atlas, parcellation_id)
    result = {
        'features': [{
            m: '{}atlases/{}/parcellations/{}/regions/{}/features/{}'.format(
                get_base_url_from_request(request),
                atlas_id.replace('/', '%2F'),
                parcellation_id.replace('/', '%2F'),
                region_id.replace('/', '%2F'),
                m
            )
        } for m in feature_modalities if issubclass(feature_classes[m], feature_export.RegionalFeature) ]
    }

    return jsonable_encoder(result)

@router.get(
    ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features/{modality}/{modality_id:path}')
def get_regional_modality_by_id(request: Request, atlas_id: str, parcellation_id: str, region_id: str, modality: str, modality_id: str, gene: Optional[str] = None):
    """
    Parameters:
        - atlas_id
        - parcellation_id
        - region_id
        - modality
        - gene

    Returns all features for a region.
    """
    regional_features=get_regional_feature(atlas_id,parcellation_id,region_id, modality, gene=gene)

    found_conn_pr = [{
        key: val() if callable(val) else val for key, val in f.items()
    } for f in regional_features if f['@id'] == modality_id ]
    
    if len(found_conn_pr) == 0:
        raise HTTPException(status_code=404, detail=f'modality with id {modality_id} not found')
    if len(found_conn_pr) != 1:
        raise HTTPException(status_code=401, detail=f'modality with id {modality_id} has multiple matches')
    return found_conn_pr[0]

@router.get(
    ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features/{modality}')
def get_feature_modality_for_region(request: Request, atlas_id: str, parcellation_id: str, region_id: str, modality: str, gene: Optional[str] = None):
    """
    Parameters:
        - atlas_id
        - parcellation_id
        - region_id
        - modality
        - gene

    Returns all features for a region.
    """

    regional_features=get_regional_feature(atlas_id,parcellation_id,region_id,modality,gene=gene)

    # in summary search, only search for basic data (filter out all keys prepended by __)
    return [{
        key: val() if callable(val) else val for key, val in f.items() if not re.search(r"^__", key)
    } for f in regional_features ]

def parse_region_selection(atlas_id: str, parcellation_id: str, region_id: str, space_id: str):
    if space_id is None:
        raise HTTPException(status_code=401, detail='space_id is required for this functionality')

    space_of_interest = siibra_spaces[space_id]
    if space_of_interest is None:
        raise HTTPException(status_code=401, detail=f'space_id {space_id} did not match any spaces')

    atlas = create_atlas(atlas_id)
    __check_and_select_parcellation(atlas,parcellation_id)
    region = find_region_via_id(atlas,region_id)
    if len(region) == 0:
        raise HTTPException(status_code=404, detail=f'cannot find region with spec {region_id}')
    if len(region) > 1:
        raise HTTPException(status_code=401, detail=f'found multiple region withs pec {region_id}')
    return (region[0], space_of_interest)

def get_path_to_regional_map(query_id, roi, space_of_interest):

    regional_map=roi.get_regional_map(space_of_interest, siibra_commons.MapType.CONTINUOUS)
    if regional_map is None:
        raise HTTPException(status_code=404, detail=f'continuous regional map for region {roi.name} cannot be found')
    
    cached_filename=str(hashlib.sha256(query_id.encode('utf-8')).hexdigest()) + '.nii.gz'

    # cache fails, fetch from source
    def save_new_nii(cached_fullpath):
        import nibabel as nib
        # fix regional_map if necessary

        regional_map.header.set_xyzt_units('mm', 'sec')

        # time series
        regional_map.header['dim'][4] = 1

        # num channel
        regional_map.header['dim'][5] = 1
        nib.save(regional_map, cached_fullpath)
        
    return get_cached_file(cached_filename, save_new_nii )
    

@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/regional_map/info')
@fanout_cache.memoize(typed=True, expire=60*60)
def get_regional_map_info(atlas_id: str, parcellation_id: str, region_id: str, space_id: Optional[str] = None):
    roi, space_of_interest = parse_region_selection(atlas_id, parcellation_id, region_id, space_id)
    query_id=f'{atlas_id}{parcellation_id}{roi.name}{space_id}'
    cached_fullpath = get_path_to_regional_map(query_id, roi, space_of_interest)
    import nibabel as nib
    import numpy as np
    nii=nib.load(cached_fullpath)
    data=nii.get_fdata()
    return {
        'min': np.min(data),
        'max': np.max(data),
    }


@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/regional_map/map')
@fanout_cache.memoize(typed=True, expire=60*60)
def get_regional_map_file(atlas_id: str, parcellation_id: str, region_id: str, space_id: Optional[str] = None):
    roi, space_of_interest = parse_region_selection(atlas_id, parcellation_id, region_id, space_id)
    query_id=f'{atlas_id}{parcellation_id}{roi.name}{space_id}'
    cached_fullpath = get_path_to_regional_map(query_id, roi, space_of_interest)
    return FileResponse(cached_fullpath, media_type='application/octet-stream')

@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}')
def get_region_by_name(request: Request, atlas_id: str, parcellation_id: str, region_id: str, space_id: Optional[str] = None):
    """
    Parameters:
        - atlas_id
        - parcellation_id
        - region_id

    Returns a specific region for a given id.
    """
    # select atlas by id
    atlas = create_atlas(atlas_id)
    # select atlas parcellation
    __check_and_select_parcellation(atlas, parcellation_id)
    region = find_region_via_id(atlas,region_id)

    if len(region) == 0:
        raise HTTPException(status_code=404, detail=f'region with spec {region_id} not found')
    r = region[0]
    region_json = create_region_json_object(r, space_id)
    _add_children_to_region(region_json, r)

    if space_id:
        atlas.select_region(r)
        # r_props = siibra_region.RegionProps(r,find_space_by_id(atlas, space_id))
        print('Space: {}'.format(find_space_by_id(atlas, space_id)))
        print('Parcellation: {}'.format(atlas.selected_region))
        print('Region: {}'.format(atlas.selected_region))
        r_props = r.spatialprops(find_space_by_id(atlas, space_id))
        region_json['props'] = {}
        region_json['props']['centroid_mm'] = list(r_props.attrs['centroid_mm'])
        region_json['props']['volume_mm'] = r_props.attrs['volume_mm']
        region_json['props']['surface_mm'] = r_props.attrs['surface_mm']
        region_json['props']['is_cortical'] = r_props.attrs['is_cortical']
    
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

@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/features/{modality}/{modality_instance_name}')
def get_single_global_feature_detail(atlas_id: str, parcellation_id: str, modality: str, modality_instance_name:str, request: Request):
    """
    Parameters:
        - atlas_id
        - parcellation_id
        - modality
        - modality_instance_name

    Returns a global feature for a parcellation.
    """
    try:
        fs=get_global_features(atlas_id, parcellation_id, modality)
        found=[f for f in fs if f['src_name'] == modality_instance_name]
        if len(found) == 0:
            raise HTTPException(status_code=404, detail=f'modality with name {modality_instance_name} not found')
        
        return {
            'result': found[0]
        }
    except NotImplementedError:
        return HTTPException(status_code=501, detail=f'modality {modality} not yet implemented')

@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/features/{modality}')
def get_single_global_feature(atlas_id: str, parcellation_id: str, modality: str, request: Request):
    """
    Parameters:
        - atlas_id
        - parcellation_id
        - modality_id

    Returns a global feature for a parcellation.
    """
    try:
        fs=get_global_features(atlas_id, parcellation_id, modality)
        return [{
            'src_name': f['src_name'],
            'src_info': f['src_info'],
        } for f in fs]
    except NotImplementedError:
        return HTTPException(status_code=501, detail=f'modality {modality} not yet implemented')

@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/features')
def get_global_features_rest(atlas_id: str, parcellation_id: str, request: Request):
    """
    Parameters:
        - atlas_id
        - parcellation_id

    Returns all global features for a parcellation.
    """

    # select atlas by id
    atlas = create_atlas(atlas_id)
    # select atlas parcellation
    __check_and_select_parcellation(atlas, parcellation_id)
    result = {
        'features': [{
            m: '{}atlases/{}/parcellations/{}/features/{}'.format(
                get_base_url_from_request(request),
                atlas_id.replace('/', '%2F'),
                parcellation_id.replace('/', '%2F'),
                m
            )
        } for m in feature_modalities if issubclass(feature_classes[m], feature_export.GlobalFeature) ]
    }

    return jsonable_encoder(result)

@router.get(ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}')
def get_parcellation_by_id(atlas_id: str, parcellation_id: str, request: Request):
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
            result = __parcellation_result_info(parcellation, atlas_id, request)
    if result:
        return jsonable_encoder(result)
    else:
        raise HTTPException(status_code=404, detail='parcellation with id: {} not found'.format(parcellation_id))


# endregion
