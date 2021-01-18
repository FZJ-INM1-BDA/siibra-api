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

from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import FileResponse

import request_utils

from brainscapes import features

router = APIRouter()

security = HTTPBearer()


class ModalityType(str, Enum):
    ReceptorDistribution = 'ReceptorDistribution'
    GeneExpression = 'GeneExpression'
    ConnectivityProfile = 'ConnectivityProfile'
    ConnectivityMatrix = 'ConnectivityMatrix'


# region === parcellations

def __parcellation_result_info(parcellation):
    return {
        "id": parcellation.id,
        "name": parcellation.name,
        "version": parcellation.version
    }

@router.get('/parcellations')
def get_all_parcellations(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Returns all parcellations that are defined in the brainscapes client.
    """
    atlas = request_utils.create_atlas()
    parcellations = atlas.parcellations
    result = []
    for parcellation in parcellations:
        result.append(__parcellation_result_info(parcellation))
    return jsonable_encoder(result)


@router.get('/parcellations/{parcellation_id}')
def get_parcellation_by_id(parcellations_id):
    """
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


@router.get('/parcellations/{parcellation_id}/regions')
def get_all_regions_for_parcellation_id(parcellations_id):
    """
    Returns all regions for a given parcellation id.
    """
    atlas = request_utils.create_atlas()
    # select atlas parcellation
    # Throw Bad Request error or 404 if bad parcellation id
    result = []
    for region in atlas.regiontree.children:
        region_json = {'name': region.name, 'children': []}
        request_utils._add_children_to_region(region_json, region)
        result.append(region_json)
    return result


# endregion

# region === spaces


@router.get('/spaces')
def get_all_spaces():
    """
    Returns all spaces that are defined in the brainscapes client.
    """
    atlas = request_utils.create_atlas()
    atlas_spaces = atlas.spaces
    result = []
    for space in atlas_spaces:
        result.append({"id": space.id, "name": space.name})
    return jsonable_encoder(result)


@router.get('/spaces/{space_id}')
def get_one_space_by_id(space_id: str):
    """
    Returns space for given id.
    """
    atlas = request_utils.create_atlas()
    space = request_utils.find_space_by_id(atlas, space_id)
    if space:
        return jsonable_encoder(space)
    else:
        raise HTTPException(status_code=404, detail='space with id: {} not found'.format(space_id))


@router.get('/spaces/{space_id}/templates')
def get_template_by_space_id(space_id):
    """
    Parameters:
    - space

    Returns all templates for a given space id.
    """
    atlas = request_utils.create_atlas()
    space = request_utils.find_space_by_id(atlas, space_id)
    template = atlas.get_template(space)

    # create file-object in memory
    # file_object = io.BytesIO()
    filename = request_utils._get_file_from_nibabel(template, 'template', space)

    return FileResponse(filename, filename=filename)


@router.get('/spaces/{space_id}/parcellation_maps')
def get_all_regions_for_parcellation_id(space_id):  # add parcellations_map_id as optional param
    """
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
        return FileResponse(mem_zip, filename='maps-{}.zip'.format(space.name.replace(' ', '_')))
    raise HTTPException(status_code=404, detail='Maps for space with id: {} not found'.format(space_id))


# endregion

# region === features


@router.get('/features')
def get_all_available_modalities():
    return [m for m in features.modalities]


@router.get('/features/{modality_id}')
def get_feature_for_modality(modality_id: ModalityType, region: str, gene: Optional[str] = None):
    if modality_id == ModalityType.ReceptorDistribution:
        return get_receptor_distribution()
    if modality_id == ModalityType.ConnectivityProfile:
        return get_connectivty_profile()
    if modality_id == ModalityType.ConnectivityMatrix:
        return get_connectivity_matrix()
    if modality_id == ModalityType.ReceptorDistribution:
        return get_receptor_distribution()

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

# @router.get('/genes')
# def genes(request: Request):
#     """
#     GET /genes
#     Parameters:
#     - region
#     - gene
#
#     Returns all genes for a given region and gene type.
#     """
#     atlas = request_utils.create_atlas()
#     selected_region = atlas.regiontree.find(request.args['region'], exact=False)
#
#     result = []
#     if request.args['gene'] in features.gene_names:
#         for region in selected_region:
#             atlas.select_region(region)
#             genes_feature = atlas.query_data(
#                 modality=features.modalities.GeneExpression,
#                 gene=request.args['gene']
#             )
#             region_result = []
#             for g in genes_feature:
#                 region_result.append(dict(
#                     expression_levels=g.expression_levels,
#                     factors=g.factors,
#                     gene=g.gene,
#                     location=g.location.tolist(),
#                     space=g.space.id,
#                     z_scores=g.z_scores
#                 ))
#             result.append(dict(
#                 region=region.name,
#                 features=region_result
#             ))
#         return jsonable_encoder(result)
#     else:
#         return 'Gene {} not found'.format(request.args['gene']), 404
