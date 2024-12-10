from typing import Union

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi_versioning import version
from fastapi_pagination import Page, paginate

from api.models.volumes.volume import MapType
from api.siibra_api_config import ROLE
from api.server import FASTAPI_VERSION, cache_header
from api.server.util import SapiCustomRoute
from api.models.volumes.parcellationmap import MapModel
from api.common import router_decorator, get_filename, logger, NotFound
from api.common.data_handlers.core.misc import (
    get_filtered_maps,
    get_single_map,
)

TAGS=["maps"]
"""HTTP map tags"""

router = APIRouter(route_class=SapiCustomRoute, tags=TAGS)
"""HTTP map router"""

@router.get("", response_model=Page[MapModel])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=get_filtered_maps)
def filter_map(parcellation_id: str=None, space_id: str=None, map_type: Union[MapType, None]=None, *, func):
    """Get a list of maps according to specification"""
    if func is None:
        raise HTTPException(500, f"func: None passsed")
    return paginate(func(parcellation_id, space_id, map_type))


@router.get("/{map_id:lazy_path}", response_model=MapModel)
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=get_single_map)
def single_map(map_id: str, *, func):
    """Get a list of maps according to specification"""
    if func is None:
        raise HTTPException(500, f"func: None passsed")
    return func(map_id)
