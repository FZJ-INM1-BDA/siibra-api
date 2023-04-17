from fastapi import APIRouter
from fastapi_pagination import paginate, Page
from fastapi_versioning import version
from typing import Optional
from functools import partial

from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.models.core.region import ParcellationEntityVersionModel
from api.common import router_decorator
from api.common.data_handlers.core.region import all_regions, single_region
from api.common.data_handlers.features.types import get_all_all_features
from api.server.util import SapiCustomRoute
from api.server.features import FeatureIdResponseModel

TAGS = ["region"]

router = APIRouter(route_class=SapiCustomRoute, tags=TAGS)

@router.get("", response_model=Page[ParcellationEntityVersionModel])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=all_regions)
def get_all_regions(parcellation_id: str, find:str=None, func=lambda:[]):
    return paginate(func(parcellation_id, find=find))

@router.get("/{region_id:lazy_path}/features", response_model=Page[FeatureIdResponseModel])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=partial(get_all_all_features, space=None))
def get_all_regions(parcellation_id: str, region_id: str, func=lambda:[]):
    return paginate(
        func(parcellation_id=parcellation_id, region_id=region_id)
    )

@router.get("/{region_id:lazy_path}", response_model=ParcellationEntityVersionModel)
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=single_region)
def get_all_regions(parcellation_id: str, region_id: str, space_id: Optional[str]=None, func=lambda:None):
    return func(parcellation_id, region_id, space_id)
