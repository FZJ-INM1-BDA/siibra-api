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

import io

import zipfile
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import FileResponse, PlainTextResponse, StreamingResponse

import request_utils

from brainscapes import features
from brainscapes.features import regionprops
from brainscapes.atlas import REGISTRY

# FastApi router to create rest endpoints
router = APIRouter()

# secure endpoints with the need to provide a bearer token
security = HTTPBearer()

# Base URL for all endpoints
ATLAS_PATH = '/atlases/{atlas_id}'


class ModalityType(str, Enum):
    """
    A class for modality type, to provide selection options to swagger
    """
    ReceptorDistribution = 'ReceptorDistribution'
    GeneExpression = 'GeneExpression'
    ConnectivityProfile = 'ConnectivityProfile'
    ConnectivityMatrix = 'ConnectivityMatrix'


def _split_id(kg_id: str):
    """
    Parameters:
        - kg_id

    Splitting the knowledge graph id into the schema and the id part.
    Only the id part is needed as a path parameter.
    """
    split_id = kg_id.split('/')
    return {
        'kg': {
            'kgSchema': '/'.join(split_id[0:-1]),
            'kgId':  split_id[-1]
        }
    }


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
            'id': a.id.replace('/', '-'),
            'name': a.name
        })
    return result


@router.get(ATLAS_PATH)
def get_all_atlases(atlas_id: str, request: Request):
    """
    Parameters:
        - atlas_id: Atlas id

    Get more information for a specific atlas with links to further objects.
    """
    atlases = REGISTRY.items
    for a in atlases:
        if a.id == atlas_id.replace('-', '/'):
            return {
                'id': a.id.replace('/', '-'),
                'name': a.name,
                'links': {
                    'parcellations': {
                        'href': '{}/parcellations'.format(request.url)
                    },
                    'spaces': {
                        'href': '{}/spaces'.format(request.url)
                    }
                }
            }
    raise HTTPException(status_code=404, detail='atlas with id: {} not found'.format(atlas_id))
# endregion


# region === parcellations

def __parcellation_result_info(parcellation):
    """
    Parameters:
        - parcellation

    Create the response for a parcellation object
    """
    result_info = {
        "id": _split_id(parcellation.id),
        "name": parcellation.name
    }
    if hasattr(parcellation, 'version') and parcellation.version:
        result_info['version'] = parcellation.version
    return result_info


@router.get(ATLAS_PATH+'/parcellations')
def get_all_parcellations(atlas_id: str, request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Parameters:
        - atlas_id

    Returns all parcellations that are defined in the brainscapes client for given atlas
    """
    print(request.headers)
    print(request.headers['accept'])
    if request.headers['accept'] == 'application/text':
        python_code = 'from brainscapes.atlas import REGISTRY \n ' \
                      'atlas = REGISTRY.MULTILEVEL_HUMAN_ATLAS \n ' \
                      'parcellations = atlas.parcellations'
        return PlainTextResponse(status_code=200, content=python_code)
    atlas = request_utils.create_atlas()
    parcellations = atlas.parcellations
    result = []
    for parcellation in parcellations:
        result.append(__parcellation_result_info(parcellation))
    return jsonable_encoder(result)


@router.get(ATLAS_PATH+'/parcellations/{parcellation_id}/regions')
def get_all_regions_for_parcellation_id(atlas_id: str, parcellations_id: str):
    """
    Parameters:
        - atlas_id
        - parcellation_id

    Returns all regions for a given parcellation id.
    """
    atlas = request_utils.create_atlas()
    # select atlas parcellation
    # Throw Bad Request error or 404 if bad parcellation id
    result = []
    for region in atlas.regiontree.children:
        region_json = request_utils.create_region_json_object(region)
        request_utils._add_children_to_region(region_json, region)
        result.append(region_json)
    return result


@router.get(ATLAS_PATH+'/parcellations/{parcellation_id}')
def get_parcellation_by_id(atlas_id: str, parcellations_id: str):
    """
    Parameters:
        - atlas_id
        - parcellation_id

    Returns one parcellation for given id or 404 Error if no parcellation is found.
    """
    atlas = request_utils.create_atlas()
    parcellations = atlas.parcellations
    result = {}
    for parcellation in parcellations:
        if parcellation.id.find(parcellations_id):
            result = __parcellation_result_info(parcellation)
    if result:
        return jsonable_encoder(result)
    else:
        raise HTTPException(status_code=404, detail='parcellation with id: {} not found'.format(parcellations_id))


# endregion

# region === spaces


@router.get(ATLAS_PATH+'/spaces')
def get_all_spaces(atlas_id: str):
    """
    Parameters:
        - atlas_id

    Returns all spaces that are defined in the brainscapes client.
    """
    atlas = request_utils.create_atlas()
    atlas_spaces = atlas.spaces
    result = []
    for space in atlas_spaces:
        result.append({
            "id": _split_id(space.id),
            "name": space.name
        })
    return jsonable_encoder(result)


@router.get(ATLAS_PATH+'/spaces/{space_id}/regions')
def get_all_regions_for_space_id(atlas_id: str, space_id: str):
    """
    Parameters:
        - atlas_id
        - space_id

    Returns all regions for a given space id.
    """
    atlas = request_utils.create_atlas()
    # select atlas parcellation
    # Throw Bad Request error or 404 if bad space id
    result = []
    for region in atlas.regiontree.children:
        region_json = request_utils.create_region_json_object(region)
        request_utils._add_children_to_region(region_json, region)
        result.append(region_json)
    return result


@router.get(ATLAS_PATH+'/spaces/{space_id}/regions/{region_id}')
def get_region_by_name(atlas_id: str, space_id: str, region_id):
    """
    Parameters:
        - atlas_id
        - space_id
        - region_id

    Returns all regions for a given space id.
    """
    atlas = request_utils.create_atlas()
    region = atlas.regiontree.find(region_id)
    # select atlas parcellation
    # Throw Bad Request error or 404 if bad space id

    r = region[0]
    region_json = request_utils.create_region_json_object(r)
    request_utils._add_children_to_region(region_json, r)
    atlas.select_region(r)
    r_props = regionprops.RegionProps(atlas, request_utils.find_space_by_id(atlas, space_id))
    region_json['props'] = {}
    region_json['props']['centroid_mm'] = list(r_props.attrs['centroid_mm'])
    region_json['props']['volume_mm'] = r_props.attrs['volume_mm']
    region_json['props']['surface_mm'] = r_props.attrs['surface_mm']
    region_json['props']['is_cortical'] = r_props.attrs['is_cortical']

    return jsonable_encoder(region_json)


@router.get(ATLAS_PATH+'/spaces/{space_id}/templates')
def get_template_by_space_id(atlas_id: str, space_id: str):
    """
    Parameters:
        - atlas_id
        - space_id

    Returns all templates for a given space id.
    """
    atlas = request_utils.create_atlas()
    space = request_utils.find_space_by_id(atlas, space_id)
    template = atlas.get_template(space)

    # create file-object in memory
    # file_object = io.BytesIO()
    filename = request_utils._get_file_from_nibabel(template, 'template', space)

    return FileResponse(filename, filename=filename)


@router.get(ATLAS_PATH+'/spaces/{space_id}/parcellation_maps')
def get_parcellation_map_for_space(atlas_id: str, space_id: str):  # add parcellations_map_id as optional param
    """
    Parameters:
        - atlas_id
        - space_id

    Returns all maps for a given space id.
    """
    atlas = request_utils.create_atlas()
    space = request_utils.find_space_by_id(atlas, space_id)
    maps = atlas.get_maps(space)
    print(maps.keys())

    if len(maps) == 1:
        filename = request_utils._get_file_from_nibabel(maps[0], 'maps', space)
        return FileResponse(filename, filename=filename)
    else:
        files = []
        mem_zip = io.BytesIO()

        for label, space_map in maps.items():
            files.append(request_utils._get_file_from_nibabel(space_map, label, space))

        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f)
                print(zf.namelist())

        mem_zip.seek(0)
        response = StreamingResponse(iter([mem_zip.getvalue()]), media_type="application/x-zip-compressed")
        response.headers["Content-Disposition"] = 'attachment; filename=maps-{}.zip'.format(space.name.replace(' ', '_'))
        return response
    raise HTTPException(status_code=404, detail='Maps for space with id: {} not found'.format(space_id))


@router.get(ATLAS_PATH+'/spaces/{space_id}')
def get_one_space_by_id(atlas_id: str, space_id: str):
    """
    Parameters:
        - atlas_id
        - space_id

    Returns space for given id.
    """
    atlas = request_utils.create_atlas()
    space = request_utils.find_space_by_id(atlas, space_id)
    if space:
        return jsonable_encoder(space)
    else:
        raise HTTPException(status_code=404, detail='space with id: {} not found'.format(space_id))


# endregion

# region === features

@router.get('/genes')
def get_gene_names():
    """
    Return all genes (name, acronym) in brainscapes
    """
    genes = features.genes.AllenBrainAtlasQuery.genes['msg']
    return jsonable_encoder([{'name': g['name'], 'acronym': g['acronym']} for g in genes])


@router.get('/genes/{gene}')
def get_gene_names(gene: str, region: str):
    """
    Parameters:
        - gene
        - region

    Return the gene expression for given gene in a given region
    """
    return get_gene_expression(region, gene)


@router.get('/features')
def get_all_available_modalities():
    """
    Return all possible modalities
    """
    return [m for m in features.modalities]


@router.get('/features/{modality_id}')
def get_feature_for_modality(modality_id: ModalityType,
                             region: str,
                             gene: Optional[str] = None,
                             credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Parameters:
        - modality_id
        - region
        - gene

    Return the feature depending on selected modality and region
    """
    if modality_id == ModalityType.ReceptorDistribution:
        return get_receptor_distribution(region)
    if modality_id == ModalityType.ConnectivityProfile:
        return get_connectivty_profile()
    if modality_id == ModalityType.ConnectivityMatrix:
        return get_connectivity_matrix()
    if modality_id == ModalityType.GeneExpression:
        return get_gene_expression(region, gene)

    raise HTTPException(status_code=400, detail='Modality: {} is not valid'.format(modality_id))


def get_receptor_distribution(region):
    receptor_data = request_utils.query_data('ReceptorDistribution', region)
    if receptor_data:
        return jsonable_encoder(receptor_data)
    else:
        raise HTTPException(status_code=404, detail='No receptor distribution found for region: {}'.format(region))


def get_gene_expression(region, gene):
    atlas = request_utils.create_atlas()
    selected_region = atlas.regiontree.find(region, exact=False)
    if not selected_region:
        raise HTTPException(status_code=400, detail='Invalid region: {}'.format(region))

    result = []
    if gene in features.gene_names:
        for region in selected_region:
            atlas.select_region(region)
            genes_feature = atlas.query_data(
                modality=features.modalities.GeneExpression,
                gene=gene
            )
            region_result = []
            for g in genes_feature:
                region_result.append(dict(
                    expression_levels=g.expression_levels,
                    factors=g.factors,
                    gene=g.gene,
                    location=g.location.tolist(),
                    space=g.space.id,
                    z_scores=g.z_scores
                ))
            result.append(dict(
                region=region.name,
                features=region_result
            ))
        return jsonable_encoder(result)
    else:
        raise HTTPException(status_code=400, detail='Invalid gene: {}'.format(gene))


def get_connectivty_profile():
    raise HTTPException(status_code=501, detail='No method yet for connectivity profile')


def get_connectivity_matrix():
    raise HTTPException(status_code=501, detail='No method yet for connectivity matrix')

# endregion

# @router.get('/receptors/fingerprint')
# def receptordata_fingerprint(request: Request):
#     """
#     GET /receptors/fingerprint
#     parameters:
#     - region
#
#     Returns a fingerprint based on the provided region.
#     """
#     if request.args and 'region' in request.args:
#         receptor_data = request_utils.query_data('ReceptorDistribution', request.args['region'])
#         return jsonable_encoder(receptor_data[0].fingerprint.__dict__)
#     else:
#         return "A region name must be provided as a query parameter", 400
#
# @router.get('/receptors/profiles')
# def receptordata_profiles(request: Request):
#     """
#     GET /receptors/profiles
#     parameters:
#     - region
#
#     Returns profles based on the provided region.
#     """
#     if request.args and 'region' in request.args:
#         receptor_data = request_utils.query_data('ReceptorDistribution', request.args['region'])
#         data = {}
#         for key, profile in receptor_data[0].profiles.items():
#             data[key] = profile
#         return jsonable_encoder(data)
#     else:
#         return "A region name must be provided as a query parameter", 400
#
# @router.get('/receptors/autoradiographs')
# def receptordata_autoradiographs(request: Request):
#     """
#     GET /receptors/autoradiographs
#     Parameters:
#     - region
#
#     Returns autoradiographs based on the provided region.
#     """
#     if request.args and 'region' in request.args:
#         receptor_data = request_utils.query_data('ReceptorDistribution', request.args['region'])
#         data = {}
#         for key, autoradiographs in receptor_data[0].autoradiographs.items():
#             data[key] = 'PLI Image'
#         return data
#     else:
#         return "A region name must be provided as a query parameter", 400
