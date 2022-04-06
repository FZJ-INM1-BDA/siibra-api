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

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from siibra.core import Parcellation, Atlas
from siibra import atlases
from siibra.features.connectivity import ConnectivityMatrixDataModel
from siibra.volumes.volume import VolumeModel
from app.service.request_utils import get_all_serializable_parcellation_features, pagination_common_params

from app.service.validation import validate_and_return_atlas, validate_and_return_parcellation
from app.core.region_api import router as region_router, get_all_regions_from_atlas_parc_space
from app.models import RestfulModel, SPyParcellationFeatureModel, SerializationErrorModel

preheat_flag = False


PARCELLATION_PATH = "/parcellations"
TAGS = ["parcellations"]

router = APIRouter(prefix=PARCELLATION_PATH)
router.include_router(region_router, prefix="/{parcellation_id:path}")


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
            response_model=SPyParcellationFeatureModel)
def get_single_detailed_global_feature(
        atlas_id: str,
        parcellation_id: str,
        feature_id: str):
    """
    Returns a global feature for a specific modality id.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)

    features = get_all_serializable_parcellation_features(parcellation)

    try:
        found_feature = [feat for feat in features if feat.model_id == feature_id][0]
        return found_feature.to_model(detail=True)
    except IndexError as err:
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
            response_model=List[SPyParcellationFeatureModel])
@SapiParcellationModel.decorate_link("features")
def get_all_global_features_for_parcellation(
    atlas_id: str,
    parcellation_id: str,
    type: Optional[str] = None,
    pagination: dict = Depends(pagination_common_params)):
    """
    Returns all global features for a parcellation.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    
    features = get_all_serializable_parcellation_features(parcellation)
    
    per_page = pagination.get("per_page")
    page = pagination.get("page")
    start_idx = per_page * page
    end_idx = per_page * (page + 1)
    return_list: List[SPyParcellationFeatureModel] = []
    for feat in features[start_idx : end_idx]:
        try:
            if type:
                if feat.get_model_type() == type:
                    return_list.append(
                        feat.to_model(detail=False)
                    )
            else:
                return_list.append(
                    feat.to_model(detail=False)
                )
        except Exception as err:
            return_list.append(
                SerializationErrorModel(message=str(err))
            )
            # some connectivity data returns
            continue
    return return_list


@router.get('/{parcellation_id:path}/volumes',
            tags=TAGS,
            response_model=List[VolumeModel])
@SapiParcellationModel.decorate_link("volumes")
def get_volumes_for_parcellation(
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
def get_single_parcellation_detail(
    atlas_id: str,
    parcellation_id: str):
    """
    Returns one parcellation for given id.
    """

    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    return SapiParcellationModel.from_parcellation(parcellation)

SapiParcellationModel.decorate_link("regions")(get_all_regions_from_atlas_parc_space)