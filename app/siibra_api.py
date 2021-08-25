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

from enum import Enum
from typing import Optional

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from siibra import features
from siibra.features import feature as feature_export

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

@router.get('/genes', tags=['data'])
def get_gene_names():
    """
    Return all genes (name, acronym) in siibra
    """
    genes = features.genes.AllenBrainAtlasQuery.GENE_NAMES
    return jsonable_encoder([{'name': genes[g], 'acronym': g}
                            for g in genes.keys()])
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


@router.get('/features', tags=['data'])
def get_all_available_modalities():
    """
    Return all possible modalities
    """
    def get_feature_type(ft):
        if issubclass(ft, feature_export.SpatialFeature):
            return 'SpatialFeature'
        if issubclass(ft, feature_export.RegionalFeature):
            return 'RegionalFeature'
        if issubclass(ft, feature_export.GlobalFeature):
            return 'GlobalFeature'
        return 'UnknownFeatureType'
    return [{
        'name': feature_name,
        'type': get_feature_type(features.registry.classes[feature_name])
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
