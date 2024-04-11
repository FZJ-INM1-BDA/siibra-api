from fastapi import APIRouter
from fastapi_pagination import paginate, Page
from fastapi_versioning import version
from typing import Optional
from functools import partial

from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.models.core.region import ParcellationEntityVersionModel, RegionRelationAsmtModel
from api.common import router_decorator
from api.common.data_handlers.core.region import all_regions, single_region, get_related_regions
from api.common.data_handlers.features.types import get_all_all_features
from api.server.util import SapiCustomRoute
from api.server.features import FeatureIdResponseModel

TAGS = ["region"]
"""HTTP region routes tags"""

router = APIRouter(route_class=SapiCustomRoute, tags=TAGS)
"""HTTP region routes router"""

@router.get("", response_model=Page[ParcellationEntityVersionModel])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=all_regions)
def get_all_regions(parcellation_id: str, find:str=None, func=lambda:[]):
    """HTTP get all regions
    
    ```python
    import siibra

    regions = [region for region in siibra.parcellations[parcellation_id]]
    ```"""
    return paginate(func(parcellation_id, find=find))

@router.get("/{region_id:lazy_path}/features", response_model=Page[FeatureIdResponseModel])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=partial(get_all_all_features, space=None))
def get_all_features_region(parcellation_id: str, region_id: str, func=lambda:[]):
    """HTTP get all features of a single region
    
    ```python
    import siibra
    
    region = siibra.get_region(parcellation_id, region_id)
    features = siibra.features.get(region, siibra.features.Feature)
    ```"""
    return paginate(
        func(parcellation_id=parcellation_id, region_id=region_id)
    )
@router.get("/{region_id:lazy_path}/related", response_model=Page[RegionRelationAsmtModel])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=get_related_regions)
def get_related_region(parcellation_id: str, region_id: str, func=lambda:[]):
    """HTTP get_related_regions of the specified region
    
    ```python
    import siibra
    region = siibra.get_region(parcellation_id, region_id)
    related_regions = [related for related in region.get_related_regions()]
    ```"""
    
    return paginate(
        func(parcellation_id=parcellation_id, region_id=region_id)
    )
    
@router.get("/{region_id:lazy_path}", response_model=ParcellationEntityVersionModel)
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=single_region)
def get_single_regions(parcellation_id: str, region_id: str, space_id: Optional[str]=None, func=lambda:None):
    """HTTP get a single region
    
    ```python
    import siibra
    region = siibra.get_region(parcellation_id, region_id)
    ```"""
    return func(parcellation_id, region_id, space_id)
