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

from siibra.core import Parcellation, Atlas
from siibra import atlases
from siibra.features.connectivity import ConnectivityMatrixDataModel
from siibra.volumes.volume import VolumeModel
from app.service.request_utils import get_all_serializable_parcellation_features

from app.service.validation import validate_and_return_atlas, validate_and_return_parcellation
from app.core.region_api import router as region_router, get_all_regions_from_atlas_parc_space
from app.models import RestfulModel

preheat_flag = False


PARCELLATION_PATH = "/parcellations"
TAGS = ["parcellations"]

router = APIRouter(prefix=PARCELLATION_PATH)
router.include_router(region_router, prefix="/{parcellation_id:path}")

UnionParcellationModels = ConnectivityMatrixDataModel


class SapiParcellationModel(Parcellation.to_model.__annotations__.get("return"), RestfulModel):
    @staticmethod
    def from_parcellation(parcellation: Parcellation) -> 'SapiParcellationModel':
        from ..app import app

        model = parcellation.to_model()
        assert len(parcellation.atlases) == 1, f"Expecting 1 and only 1 set of atlases associated with {str(parcellation)}, but got {len(parcellation.atlases)}"
        atlas: Atlas = list(parcellation.atlases)[0]
        
        return SapiParcellationModel(
            **model.dict(),
            links=SapiParcellationModel.create_links(atlas_id=atlas.to_model().id, parcellation_id=model.id)
        )


@router.get("",
    tags=TAGS,
    response_model=List[SapiParcellationModel])
def get_all_parcellations(atlas_id: str):
    """
    Returns all parcellations that are defined in the siibra client for given atlas.
    """
    try:
        atlas = atlases[atlas_id]
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"atlas with id: {atlas_id} not found."
        )
    
    return [SapiParcellationModel.from_parcellation(p) for p in atlas.parcellations]


@router.get('/{parcellation_id:path}/features/{feature_id}',
            tags=TAGS,
            response_model=UnionParcellationModels)
def get_single_global_feature_detail(
        atlas_id: str,
        parcellation_id: str,
        feature_id: str):
    """
    Returns a global feature for a specific modality id.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)

    try:
        features = get_all_serializable_parcellation_features(parcellation)
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


@router.get('/{parcellation_id:path}/features',
            tags=TAGS,
            response_model=List[UnionParcellationModels])
@SapiParcellationModel.decorate_link("features")
def get_global_features_names(
    atlas_id: str,
    parcellation_id: str):
    """
    Returns all global features for a parcellation.
    """

    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    
    features = get_all_serializable_parcellation_features(parcellation)
    return [f.to_model(detail=False) for f in features]


@router.get('/{parcellation_id:path}/volumes',
            tags=TAGS,
            response_model=List[VolumeModel])
@SapiParcellationModel.decorate_link("volumes")
def get_volumes_by_id(
    atlas_id: str,
    parcellation_id: str):
    """
    Returns one parcellation for given id.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    return [vol.to_model() for vol in parcellation.volumes]


@router.get('/{parcellation_id:path}',
            tags=TAGS,
            response_model=SapiParcellationModel)
@SapiParcellationModel.decorate_link("self")
def get_parcellation_by_id(
    atlas_id: str,
    parcellation_id: str):
    """
    Returns one parcellation for given id.
    """

    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    return SapiParcellationModel.from_parcellation(parcellation)

SapiParcellationModel.decorate_link("regions")(get_all_regions_from_atlas_parc_space)