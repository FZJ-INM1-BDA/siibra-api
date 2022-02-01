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

from typing import List
from fastapi import APIRouter, HTTPException

import siibra
from siibra.core.serializable_concept import JSONSerializable
from siibra.core import Parcellation
from siibra import atlases
from siibra.features.connectivity import ConnectivityMatrixDataModel
from siibra.features.feature import ParcellationFeature
from siibra.features import modalities, FeatureQuery

from app.service.validation import validate_and_return_atlas, validate_and_return_parcellation, FeatureIdNameModel
from app.core.region_api import router as region_router

preheat_flag = False


PARCELLATION_PATH = "/parcellations"
TAGS = ["parcellations"]

router = APIRouter(prefix=PARCELLATION_PATH)
router.include_router(region_router, prefix="/{parcellation_id:path}")

UnionParcellationModels = ConnectivityMatrixDataModel


@router.get("",
    tags=TAGS,
    response_model=List[Parcellation.to_model.__annotations__.get("return")])
def get_all_parcellations(atlas_id: str):
    """
    Returns all parcellations that are defined in the siibra client for given atlas.
    """
    try:
        atlas = atlases[atlas_id]
    except Exception:
        return HTTPException(
            status_code=404,
            detail=f"atlas with id: {atlas_id} not found."
        )
    
    return [p.to_model() for p in atlas.parcellations]


@router.get('/{parcellation_id:path}/features/{modality_id}/{feature_id}',
            tags=TAGS,
            response_model=UnionParcellationModels)
def get_single_global_feature_detail(
        atlas_id: str,
        parcellation_id: str,
        modality_id: str,
        feature_id: str):
    """
    Returns a global feature for a specific modality id.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    try:
        features = siibra.get_features(parcellation, modality_id)
        assert all(isinstance(feature, JSONSerializable) for feature in features), f"Expecting all features are jsonserializable"
        models: List[UnionParcellationModels] = [feature.to_model() for feature in features]
        filtered_models = [mod for mod in models if mod.id == feature_id]
        return filtered_models[0]
    except IndexError:
        raise HTTPException(
            status_code=404,
            detail=f"cannot find feature_id {feature_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal Error. {str(e)}"
        )


@router.get('/{parcellation_id:path}/features/{modality_id}',
            tags=TAGS,
            response_model=List[UnionParcellationModels])
def get_single_global_feature(
    atlas_id: str,
    parcellation_id: str,
    modality_id: str):
    """
    Returns a global feature for a parcellation, filtered by given modality.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    try:
        features = siibra.get_features(parcellation, modality_id)
        assert all(isinstance(feature, JSONSerializable) for feature in features), f"Expecting all features are jsonserializable"
        return [feature.to_model() for feature in features]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal Error. {str(e)}"
        )

@router.get('/{parcellation_id:path}/features',
            tags=TAGS,
            response_model=List[FeatureIdNameModel])
def get_global_features_names(
    atlas_id: str,
    parcellation_id: str):
    """
    Returns all global features for a parcellation.
    """
    return_list = []
    for modality, query_list in [(modality, FeatureQuery._implementations[modality]) for modality in modalities]:
        implemented_flag = all(issubclass(query._FEATURETYPE, JSONSerializable) for query in query_list)
        if all(issubclass(query._FEATURETYPE, ParcellationFeature) for query in query_list):
            return_list.append({
                "@id": modality,
                "name": modality,
                "nyi": not implemented_flag,
            })
    return return_list


@router.get('/{parcellation_id:path}',
            tags=TAGS,
            response_model=Parcellation.to_model.__annotations__.get("return"))
def get_parcellation_by_id(
    atlas_id: str,
    parcellation_id: str):
    """
    Returns one parcellation for given id.
    """
    try:
        atlas = atlases[atlas_id]
        parcellation = atlas.parcellations[parcellation_id]
        return parcellation.to_model()
    except IndexError as e:
        return HTTPException(
            status_code=404,
            detail=f"atlas_id {atlas_id} parcellation_id {parcellation_id} not found. {str(e)}"
        )
