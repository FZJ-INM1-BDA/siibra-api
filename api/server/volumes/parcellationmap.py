from fastapi import APIRouter, HTTPException
from fastapi_pagination import paginate, Page
from fastapi_versioning import version

from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.models.volumes.parcellationmap import MapModel
from api.models.volumes.volume import MapType
from api.common import router_decorator
from api.common.data_handlers.volumes.parcellationmap import get_map
from api.server.util import SapiCustomRoute

TAGS=["maps"]

router = APIRouter(route_class=SapiCustomRoute, tags=TAGS)

@router.get("", response_model=MapModel)
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=get_map)
def get_map(parcellation_id: str, space_id: str, map_type: MapType, *, func):
    if func is None:
        raise HTTPException(500, f"func: None passsed")
    return func(parcellation_id, space_id, map_type)

