from typing import Callable, List, Optional, Tuple, Union

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.responses import FileResponse

import siibra
from siibra.core import Region
from siibra.features.receptors import ReceptorDatasetModel
from siibra.features import FeatureQuery, modalities
from siibra.features.feature import RegionalFeature
from siibra.core.datasets import DatasetJsonModel
from siibra.core.serializable_concept import JSONSerializable

from app.configuration.diskcache import memoize
from app.service.request_utils import get_path_to_regional_map
from app import logger
from app.service.validation import (
    validate_and_return_atlas,
    validate_and_return_parcellation,
    validate_and_return_region,
    validate_and_return_space,
    file_response_openapi,
    FeatureIdNameModel,
)

REGION_PATH = "/regions"

router = APIRouter(prefix=REGION_PATH)

TAGS=["regions"]


# this is required, otherwise, Union operation collapses it to DatasetJsonModel
class BaseDatasetJsonModel(DatasetJsonModel): pass

UnionRegionalFeatureModels = Union[
    ReceptorDatasetModel,
    BaseDatasetJsonModel,
]


@router.get("", tags=TAGS,
            response_model=List[Region.to_model.__annotations__.get("return")])
def get_all_regions_from_atlas_parc_space(
    atlas_id: str,
    parcellation_id: str,
    space_id: Optional[str] = None):
    """
    Returns all regions for a given parcellation id.
    """
    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id, atlas)
    space = validate_and_return_space(space_id, atlas) if space_id else None
    return [r.to_model(space=space) for r in parcellation.regiontree]


@router.get("/{region_id:path}/features",
            tags=TAGS,
            response_model=List[FeatureIdNameModel])
def get_all_features_for_region(
    atlas_id: str,
    parcellation_id: str,
    region_id: str,
    space_id: Optional[str]=None):
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

    return_list = []
    for modality, query_list in [(modality, FeatureQuery._implementations[modality]) for modality in modalities]:
        if all(issubclass(query._FEATURETYPE, RegionalFeature) for query in query_list):
            implemented_flag = all(issubclass(query._FEATURETYPE, JSONSerializable) for query in query_list)
            return_list.append({
                "@id": modality,
                "name": modality,
                "nyi": not implemented_flag
            })
    return return_list

@router.get("/{region_id:path}/features/{modality_id}/{feature_id:path}",
            tags=TAGS,
            response_model=UnionRegionalFeatureModels)
@memoize(typed=True)
def get_regional_modality_by_id(
    atlas_id: str,
    parcellation_id: str,
    region_id: str,
    modality_id: str,
    feature_id: str,
    space_id: Optional[str]=None,
    gene: Optional[str]=None):
    """
    Returns a feature for a region, as defined by by the modality and feature ID
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

    features = siibra.get_features(region, modality=modality_id)
    filtered_features = [feature for feature in features if feature.to_model(detail=False).id == feature_id]
    try:
        return filtered_features[0].to_model(detail=True).dict()
    except IndexError:
        raise HTTPException(
            status_code=404,
            detail=f"cannot find feature with id {feature_id}"
        )


@router.get("/{region_id:path}/features/{modality_id}",
            tags=TAGS,
            response_model=List[UnionRegionalFeatureModels])
@memoize(typed=True)
def get_feature_modality_for_region(
    atlas_id: str,
    parcellation_id: str,
    region_id: str,
    modality_id: str,
    space_id: Optional[str] = None,
    gene: Optional[str] = None):
    """
    Returns list of the features for a region, as defined by the modality.
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

    features = siibra.get_features(region, modality=modality_id)
    return [feature.to_model(detail=False) for feature in features]


def regional_map_route_decorator():
    """
    Return the full path to the requested regional map (Probabilistic map).
    If does not exist, will download and cache the result.
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
            logger.debug(f'queryId: {query_id}')
            cached_fullpath = get_path_to_regional_map(query_id, region, space)
            logger.debug(f'cached path: {cached_fullpath}')
            return fn(cached_fullpath)

        inner.__name__ = fn.__name__
        inner.__doc__ = fn.__doc__

        return inner
    return outer


class NiiMetadataModel(BaseModel):
    min: float
    max: float


@router.get("/{region_id:path}/regional_map/info",
            tags=TAGS,
            response_model=NiiMetadataModel)
@memoize(typed=True)
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
        'min': np.min(data),
        'max': np.max(data),
    }


@router.get("/{region_id:path}/regional_map/map",
            tags=TAGS,
            responses=file_response_openapi)
@regional_map_route_decorator()
def get_regional_map_file(cached_fullpath: str):
    """
    Returns a regional map for given region name.
    """
    return FileResponse(cached_fullpath, media_type='application/octet-stream')


@router.get("/{region_id:path}",
            tags=TAGS,
            response_model=Region.to_model.__annotations__.get("return"))
def get_single_region_detail(
    atlas_id: str,
    parcellation_id: str,
    region_id: str,
    space_id: Optional[str] = None):

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