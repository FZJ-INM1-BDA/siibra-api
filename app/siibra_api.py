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

from .request_utils import query_data, create_atlas, find_region_via_id

from siibra import features, modalities
from siibra.features import feature as feature_export,classes as feature_classes, connectivity as connectivity_export, receptors as receptors_export
from memoization import cached

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
    Return all genes (name, acronym) in siibra
    """
    print(dir(features.genes.AllenBrainAtlasQuery))
    genes = features.genes.AllenBrainAtlasQuery.GENE_NAMES
    return jsonable_encoder([{'name': genes[g], 'acronym': g} for g in genes.keys()])
#
#
# @router.get('/genes/{gene}')
# def get_gene_expression_for_region(gene: str, region: str):
#     """
#     Parameters:
#         - gene
#         - region
#
#     Return the gene expression for given gene in a given region
#     """
#     return get_gene_expression(region, gene)


@router.get('/features')
def get_all_available_modalities():
    """
    Return all possible modalities
    """
    def get_feature_type(ft):
        if issubclass(ft,feature_export.SpatialFeature):
            return 'SpatialFeature'
        if issubclass(ft,feature_export.RegionalFeature):
            return 'RegionalFeature'
        if issubclass(ft,feature_export.GlobalFeature):
            return 'GlobalFeature'
        return 'UnknownFeatureType'
    return [{
        'name': feature_name,
        'type': get_feature_type(feature_classes[feature_name])
    } for feature_name in features.modalities]
#
#
# @router.get('/features/{modality_id}')
# def get_feature_for_modality(modality_id: ModalityType,
#                              region: str,
#                              gene: Optional[str] = None):
#     """
#     Parameters:
#         - modality_id
#         - region
#         - gene
#
#     Return the feature depending on selected modality and region
#     """
#     if modality_id == ModalityType.ReceptorDistribution:
#         return get_receptor_distribution(region)
#     if modality_id == ModalityType.ConnectivityProfile:
#         return get_connectivty_profile()
#     if modality_id == ModalityType.ConnectivityMatrix:
#         return get_connectivity_matrix()
#     if modality_id == ModalityType.GeneExpression:
#         return get_gene_expression(region, gene)
#
#     raise HTTPException(status_code=400, detail='Modality: {} is not valid'.format(modality_id))

def get_gene_expression(atlas_id, region_id, gene):
    atlas = create_atlas(atlas_id)
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

@cached
def get_regional_feature(atlas_id,parcellation_id,region_id,modality_id):
    # select atlas by id
    if modality_id not in feature_classes:
        # modality_id not found in feature_classes
        return []
    
    if not issubclass(feature_classes[modality_id], feature_export.RegionalFeature):
        # modality_id is not a global feature, return empty array
        return []

    # select atlas by id
    atlas = create_atlas(atlas_id)
    # select atlas parcellation
    try:
        # select atlas parcellation
        atlas.select_parcellation(parcellation_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail='The requested parcellation is not supported by the selected atlas.'
        )
    regions = find_region_via_id(atlas,region_id)

    if len(regions) == 0:
        raise HTTPException(status_code=404, detail=f'Region with id {region_id} not found!')
    
    atlas.select_region(regions[0])
    got_features=atlas.get_features(modality_id)
    if feature_classes[modality_id] == connectivity_export.ConnectivityProfile:
        return [{
            "@id": conn_pr.src_name,
            "src_name": conn_pr.src_name,
            "src_info": conn_pr.src_info,
            "__column_names": conn_pr.column_names,
            "__profile": conn_pr.profile,
        } for conn_pr in got_features ]
    if feature_classes[modality_id] == receptors_export.ReceptorDistribution:
        return [{
            "@id": receptor_pr.name,
            "name": receptor_pr.name,
            "info": receptor_pr.info,
            "__receptor_symbols": receptors_export.RECEPTOR_SYMBOLS,
            "__files": receptor_pr.files,
            "__data": {
                "__profiles": receptor_pr.profiles,
                "__autoradiographs": receptor_pr.autoradiographs,
                "__fingerprint": receptor_pr.fingerprint,
                "__profile_unit": receptor_pr.profile_unit,
            },
        } for receptor_pr in got_features ]
    raise NotImplementedError(f'feature {modality_id} has not yet been implmented')

@cached
def get_global_features(atlas_id,parcellation_id,modality_id):
    # select atlas by id
    if modality_id not in feature_classes:
        # modality_id not found in feature_classes
        return []
    
    if not issubclass(feature_classes[modality_id], feature_export.GlobalFeature):
        # modality_id is not a global feature, return empty array
        return []

    atlas = create_atlas(atlas_id)
    # select atlas parcellation
    atlas.select_parcellation(parcellation_id)
    got_features=atlas.get_features(modality_id)
    if feature_classes[modality_id] == connectivity_export.ConnectivityMatrix:
        return [{
            'src_name': f.src_name,
            'src_info': f.src_info,
            'column_names': f.column_names,
            'matrix': f.matrix.tolist(),
        } for f in got_features ]
    raise NotImplementedError(f'feature {modality_id} has not yet been implmented')


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
