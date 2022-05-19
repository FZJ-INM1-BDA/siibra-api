# Copyright 2018-2022 Institute of Neuroscience and Medicine (INM-1),
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

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi_versioning import version
import siibra
from siibra.core.serializable_concept import JSONSerializable

from app import FASTAPI_VERSION

router = APIRouter()


@router.get("/genes", tags=["data"])
@version(*FASTAPI_VERSION)
def get_gene_names():
    """
    Return all genes (name, acronym) in siibra
    """
    genes = []
    for gene in siibra.features.gene_names:
        genes.append(gene)
    return jsonable_encoder({"genes": genes})


@router.get("/modalities", tags=["data"])
@version(*FASTAPI_VERSION)
def get_all_available_modalities():
    """
    Return all possible modalities
    """
    return [{
        "name": feature_name,
        "types": set([ FeatureQuery._FEATURETYPE.get_model_type()
            for FeatureQuery in siibra.features.FeatureQuery._implementations[feature_name]
            if issubclass(FeatureQuery._FEATURETYPE, JSONSerializable) ])
    } for feature_name in siibra.features.modalities]

