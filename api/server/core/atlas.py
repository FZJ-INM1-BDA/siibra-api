from fastapi import APIRouter, HTTPException
from fastapi_pagination import paginate, Page
from fastapi_versioning import version

from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.models.core.atlas import SiibraAtlasModel
from api.common import router_decorator
from api.common.data_handlers.core.atlas import all_atlases, single_atlas
from api.server.util import SapiCustomRoute

TAGS=["atlas"]
"""HTTP atlas routes tags"""

router = APIRouter(route_class=SapiCustomRoute)
"""HTTP atlas routes router"""

@router.get("", tags=TAGS, response_model=Page[SiibraAtlasModel])
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=all_atlases)
def get_all_atlases(*, func):
    """HTTP get all atlases"""
    if func is None:
        raise HTTPException(500, "func: None passed")
    return paginate(func())

@router.get("/{atlas_id:lazy_path}", tags=TAGS, response_model=SiibraAtlasModel)
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=single_atlas)
def get_single_atlas(atlas_id: str, *, func):
    """HTTP get a single atlas"""
    if func is None:
        raise HTTPException(500, "func: None passed")
    return func(atlas_id)
