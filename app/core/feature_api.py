from typing import Callable, List, Optional, Tuple, Union

from fastapi import APIRouter, HTTPException
from fastapi_versioning import version

from siibra.features import FeatureQuery

from app import FASTAPI_VERSION
from app.core.region_api import UnionRegionalFeatureModels
from app.core.space_api import UnionSpatialFeatureModels
from app.models import SPyParcellationFeatureModel

FeatureModels = Union[
    UnionRegionalFeatureModels,
    UnionSpatialFeatureModels,
    SPyParcellationFeatureModel,
]


FEATURE_PATH = "/features"

router = APIRouter(prefix=FEATURE_PATH)

TAGS=["features"]


@router.get("/{feature_id:lazy_path}", tags=TAGS,
            response_model=FeatureModels)
@version(*FASTAPI_VERSION)
def get_feature_details(feature_id: str,
                        atlas_id: Optional[str] = None,
                        space_id: Optional[str] = None,
                        parcellation_id: Optional[str] = None,
                        region_id: Optional[str] = None):
    """
    Get all details for one feature by id.
    Since the feature id is unique, no atlas concept is required.

    Further optional params can extend the result.
    :param feature_id:
    :param atlas_id:
    :param space_id:
    :param parcellation_id:
    :param region_id:
    :return: FeatureModels
    """
    feature = FeatureQuery.get_feature_by_id(feature_id)
    if feature is not None:
        return feature.to_model(detail=True)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Feature with id {feature_id} could not be found"
        )
