from fastapi import APIRouter, HTTPException
from fastapi_pagination import paginate, Page
from fastapi_versioning import version

from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.models.core.space import CommonCoordinateSpaceModel
from api.common import router_decorator
from api.common.data_handlers.core.space import all_spaces, single_space
from api.server.util import SapiCustomRoute

TAGS = ["space"]

router = APIRouter(route_class=SapiCustomRoute, tags=TAGS)


@router.get("", response_model=Page[CommonCoordinateSpaceModel])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=all_spaces)
def get_all_spaces(*, func):
    if func is None:
        raise HTTPException(500, f"func: None passed")
    return paginate(func())

@router.get("/{space_id:lazy_path}", response_model=CommonCoordinateSpaceModel)
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=single_space)
def get_single_space(space_id: str, *, func):
    if func is None:
        raise HTTPException(500, f"func: None passsed")
    return func(space_id)