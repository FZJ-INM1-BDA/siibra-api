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

from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder

from .request_utils import query_data, create_atlas

from brainscapes import features

# FastApi router to create rest endpoints
router = APIRouter()

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


# region === features

@router.get('/genes')
def get_gene_names():
    """
    Return all genes (name, acronym) in brainscapes
    """
    genes = features.genes.AllenBrainAtlasQuery.genes['msg']
    return jsonable_encoder([{'name': g['name'], 'acronym': g['acronym']} for g in genes])


@router.get('/genes/{gene}')
def get_gene_expression_for_region(gene: str, region: str):
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
                             gene: Optional[str] = None):
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
    receptor_data = query_data('ReceptorDistribution', region)
    if receptor_data:
        return jsonable_encoder(receptor_data)
    else:
        raise HTTPException(status_code=404, detail='No receptor distribution found for region: {}'.format(region))


def get_gene_expression(region, gene):
    atlas = create_atlas()
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
