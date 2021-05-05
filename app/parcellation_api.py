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
from starlette.responses import PlainTextResponse
from fastapi.encoders import jsonable_encoder
from .atlas_api import ATLAS_PATH
from .request_utils import split_id, create_atlas, create_region_json_object, create_region_json_object_tmp, \
    _add_children_to_region, find_space_by_id, find_region_via_id
from .request_utils import get_spaces_for_parcellation, get_base_url_from_request
from siibra import region as siibra_region
from siibra.features import feature as feature_export,classes as feature_classes,modalities as feature_modalities
from .siibra_api import get_receptor_distribution, get_global_features, get_regional_feature, get_gene_expression
import re
from memoization import cached

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
        }}
    if hasattr(parcellation, 'version') and parcellation.version:
        result_info['version'] = parcellation.version
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
@cached
def get_all_regions_for_parcellation_id(atlas_id: str, parcellation_id: str, space_id: Optional[str] = None):
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
    atlas.select_parcellation(parcellation_id)
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
    ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features/{modality:path}/{modality_id:path}')
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
    regional_features=get_regional_feature(atlas_id,parcellation_id,region_id, modality)
    found_conn_pr = [ conn_pr for conn_pr in regional_features if conn_pr['@id'] == modality_id ]
    if len(found_conn_pr) == 0:
        raise HTTPException(status_code=404, detail=f'modality with id {modality_id} not found')
    if len(found_conn_pr) != 1:
        raise HTTPException(status_code=401, detail=f'modality with id {modality_id} has multiple matches')
    return found_conn_pr[0]

@router.get(
    ATLAS_PATH + '/{atlas_id:path}/parcellations/{parcellation_id:path}/regions/{region_id:path}/features/{modality:path}')
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

    if modality == ModalityType.GeneExpression:
        return get_gene_expression(region_id, gene)

    regional_features=get_regional_feature(atlas_id,parcellation_id,region_id,modality)

    # in summary search, only search for basic data (filter out all keys prepended by __)
    return [{
        key: val for key, val in f.items() if not re.search(r"^__", key)
    } for f in regional_features ]

    raise HTTPException(status_code=400, detail='Modality: {} is not valid'.format(modality))


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
    atlas.select_parcellation(parcellation_id)
    region = find_region_via_id(atlas,region_id)

    if len(region) == 0:
        raise HTTPException(status_code=404, detail=f'region with spec {region_id} not found')
    r = region[0]
    region_json = create_region_json_object(r)
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
    region_json['links'] = {
        'features': '{}atlases/{}/parcellations/{}/regions/{}/features'.format(
            get_base_url_from_request(request),
            atlas_id.replace('/', '%2F'),
            parcellation_id.replace('/', '%2F'),
            region_id.replace('/', '%2F')
        )
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
    atlas.select_parcellation(parcellation_id)
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
