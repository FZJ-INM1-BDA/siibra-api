from typing import Callable, List, Optional, Tuple, Union

from fastapi import APIRouter, HTTPException

import siibra
from siibra.features import FeatureQuery, modalities


from app.core.region_api import UnionRegionalFeatureModels


FEATURE_PATH = "/features"

router = APIRouter(prefix=FEATURE_PATH)

TAGS=["features"]


@router.get("/{feature_id:path}", tags=TAGS,
            response_model=UnionRegionalFeatureModels)
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
    :return: UnionRegionalFeatureModels
    """
    raise HTTPException(
        status_code=501,
        detail=f"Not yet implemented"
    )