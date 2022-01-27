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
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
import siibra


router = APIRouter()


@router.get('/genes', tags=['data'])
def get_gene_names():
    """
    Return all genes (name, acronym) in siibra
    """
    # genes = features.genes.AllenBrainAtlasQuery.GENE_NAMES
    genes = []
    for gene in siibra.features.gene_names:
        genes.append(gene)
    return jsonable_encoder({'genes': genes})


@router.get('/features', tags=['data'])
def get_all_available_modalities():
    """
    Return all possible modalities
    """
    def get_feature_type(ft):
        if issubclass(ft, siibra.features.feature.SpatialFeature):
            return 'SpatialFeature'
        if issubclass(ft, siibra.features.feature.RegionalFeature):
            return 'RegionalFeature'
        if issubclass(ft, siibra.features.feature.ParcellationFeature):
            return 'ParcellationFeature'
        return 'UnknownFeatureType'
    return [{
        'name': feature_name.modality(),
        'type': get_feature_type(feature_name._FEATURETYPE)
    } for feature_name in siibra.features.modalities]

