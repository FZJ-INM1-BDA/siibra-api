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

from typing import Callable, List, Optional, Tuple, Union

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.responses import FileResponse

from siibra.core import Region
from siibra.features.receptors import ReceptorDatasetModel
from siibra.features.cells import CorticalCellDistributionModel
from siibra.core.datasets import DatasetJsonModel

from app.service.request_utils import get_all_serializable_regional_features, get_path_to_regional_map
from app import logger
from app.service.validation import (
    validate_and_return_atlas,
    validate_and_return_parcellation,
    validate_and_return_region,
    validate_and_return_space,
    file_response_openapi,
)

REGION_PATH = "/regions"

router = APIRouter(prefix=REGION_PATH)

TAGS = ["regions"]


# this is required, otherwise, Union operation collapses it to DatasetJsonModel
class BaseDatasetJsonModel(DatasetJsonModel):
    pass


UnionRegionalFeatureModels = Union[
    ReceptorDatasetModel,
    BaseDatasetJsonModel,
    CorticalCellDistributionModel,
]


@router.get("", tags=TAGS,
            response_model=List[Region.to_model.__annotations__.get("return")])
def get_all_regions_from_atlas_parc_space(
    atlas_id: str,
    parcellation_id: str,
    space_id: Optional[str] = None,
    find:  Optional[str] = None):
    """
    Returns all regions for a given parcellation id.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    space = validate_and_return_space(space_id, atlas) if space_id else None
    if find is None:
        return [r.to_model(space=space) for r in parcellation.regiontree]
    else:
        return [r.to_model(space=space) for r in parcellation.find_regions(find)]



@router.get("/{region_id:lazy_path}/features",
            tags=TAGS,
            response_model=List[UnionRegionalFeatureModels])
def get_all_regional_features_for_region(
    atlas_id: str,
    parcellation_id: str,
    region_id: str,
    space_id: Optional[str]=None,
    type: Optional[str]=None):
    """
    Returns all regional features for a region.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    region = validate_and_return_region(region_id, parcellation)
    space = validate_and_return_space(space_id, atlas) if space_id else None
    if space and (space not in region.supported_spaces):
        raise HTTPException(
            status_code=400,
            detail=f"space {str(space)} is not supported by region {str(region)}"
        )
    if not type:
        return [feat.to_model(space=space) for feat in get_all_serializable_regional_features(region, space)]
    else:
        return [feat.to_model(space=space) for feat in get_all_serializable_regional_features(region, space) if feat.to_model().type == type]


@router.get("/{region_id:lazy_path}/features/{feature_id:lazy_path}",
            tags=TAGS,
            response_model=UnionRegionalFeatureModels)
def get_single_detailed_regional_feature(
    atlas_id: str,
    parcellation_id: str,
    region_id: str,
    feature_id: str,
    space_id: Optional[str]=None,
    gene: Optional[str]=None):
    """
    Returns a feature for a region, as defined by the modality and feature ID
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    region = validate_and_return_region(region_id, parcellation)
    space = validate_and_return_space(space_id, atlas) if space_id else None
    if space and (space not in region.supported_spaces):
        raise HTTPException(
            status_code=400,
            detail=f"space {str(space)} is not supported by region {str(region)}"
        )

    found_feat = [feat for feat in get_all_serializable_regional_features(region, space) if feat.model_id == feature_id]
    try:
        return found_feat[0].to_model(detail=True, space=space)
    except IndexError:
        raise HTTPException(
            status_code=404,
            detail=f"cannot find feature with id {feature_id}"
        )


def regional_map_route_decorator():
    """
    Return the full path to the requested regional map (Probabilistic map).
    If it does not exist, will download and cache the result.
    """
    def outer(fn: Callable):
        def inner(
            atlas_id: str,
            parcellation_id: str,
            region_id: str,
            space_id: Optional[str] = None
        ):

            atlas = validate_and_return_atlas(atlas_id)
            parcellation = validate_and_return_parcellation(parcellation_id, atlas)
            region = validate_and_return_region(region_id, parcellation)

            if space_id is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"space_id is required"
                )
            space = validate_and_return_space(space_id, atlas) if space_id else None
            if space and (space not in region.supported_spaces):
                raise HTTPException(
                    status_code=400,
                    detail=f"space {str(space)} is not supported by region {str(region)}"
                )

            query_id = f"{atlas.id}{parcellation.id}{region.id}{space.id}"
            logger.debug(f"queryId: {query_id}")
            cached_fullpath = get_path_to_regional_map(query_id, region, space)
            logger.debug(f"cached path: {cached_fullpath}")
            return fn(cached_fullpath)

        inner.__name__ = fn.__name__
        inner.__doc__ = fn.__doc__

        return inner
    return outer


class NiiMetadataModel(BaseModel):
    min: float
    max: float


@router.get("/{region_id:lazy_path}/regional_map/info",
            tags=TAGS,
            response_model=NiiMetadataModel)
@regional_map_route_decorator()
def get_regional_map_info(cached_fullpath: str):
    """
    Returns information about a regional map for given region name.
    """
    import nibabel as nib
    import numpy as np
    
    nii = nib.load(cached_fullpath)
    data = nii.get_fdata()
    return {
        "min": np.min(data),
        "max": np.max(data),
    }


@router.get("/{region_id:lazy_path}/regional_map/map",
            tags=TAGS,
            responses=file_response_openapi)
@regional_map_route_decorator()
def get_regional_map_file(cached_fullpath: str):
    """
    Returns a regional map for given region name.
    """
    return FileResponse(cached_fullpath, media_type="application/octet-stream")


@router.get("/{region_id:lazy_path}",
            tags=TAGS,
            response_model=Region.to_model.__annotations__.get("return"))
def get_single_region_detail(atlas_id: str, parcellation_id: str, region_id: str, space_id: Optional[str] = None):
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    region = validate_and_return_region(region_id, parcellation)
    space = validate_and_return_space(space_id, atlas) if space_id else None
    if space and (space not in region.supported_spaces):
        raise HTTPException(
            status_code=400,
            detail=f"space {str(space)} is not supported by region {str(region)}"
        )
    return region.to_model(detail=True, space=space)
