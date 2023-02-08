from fastapi import APIRouter, HTTPException
from fastapi_pagination import paginate, Page
from fastapi_versioning import version

from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.models.core.parcellation import SiibraParcellationModel
from api.common import router_decorator
from api.common.data_handlers.core.parcellation import all_parcellations, single_parcellation
from api.server.util import SapiCustomRoute

TAGS = ["parcellation"]

router = APIRouter(route_class=SapiCustomRoute, tags=TAGS)

@router.get("", response_model=Page[SiibraParcellationModel])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=all_parcellations)
def get_all_parcellations(func):
    if func is None:
        raise HTTPException(500, f"func: None passed")
    return paginate(func())

@router.get("/{parcellation_id:lazy_path}", response_model=SiibraParcellationModel)
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=single_parcellation)
def get_single_parcellation(parcellation_id: str, *, func):
    if func is None:
        raise HTTPException(500, f"func: None passsed")
    return func(parcellation_id)

