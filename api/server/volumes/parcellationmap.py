from pydantic import BaseModel

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi_versioning import version

from api.server import FASTAPI_VERSION
from api.siibra_api_config import ROLE
from api.models.volumes.parcellationmap import MapModel
from api.models.volumes.volume import MapType
from api.common import router_decorator, get_filename, logger
from api.common.data_handlers.volumes.parcellationmap import get_map, get_region_statistic_map, get_region_statistic_map_info, get_parcellation_labelled_map
from api.server.util import SapiCustomRoute
import os

TAGS=["maps"]

router = APIRouter(route_class=SapiCustomRoute, tags=TAGS)

@router.get("", response_model=MapModel)
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=get_map)
def route_get_map(parcellation_id: str, space_id: str, map_type: MapType, *, func):
    if func is None:
        raise HTTPException(500, f"func: None passsed")
    return func(parcellation_id, space_id, map_type)


@router.get("/labelled_map.nii.gz", response_class=FileResponse, tags=TAGS)
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=get_parcellation_labelled_map)
def route_get_parcellation_labelled_map(parcellation_id: str, space_id: str, *, func):
    if func is None:
        raise HTTPException(500, f"func: None passsed")
    
    headers={
        "content-type": "application/octet-stream",
        "content-disposition": f'attachment; filename="labelled_map.nii.gz"'
    }

    full_filename = func(parcellation_id, space_id)
    assert os.path.isfile(full_filename), f"file saved incorrectly"
    return FileResponse(full_filename, headers=headers)


@router.get("/statistical_map.nii.gz", response_class=FileResponse, tags=TAGS)
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=get_region_statistic_map)
def route_get_region_statistical_map(parcellation_id: str, space_id: str, region_id: str, *, func):
    if func is None:
        raise HTTPException(500, f"func: None passsed")
    
    headers={
        "content-type": "application/octet-stream",
        "content-disposition": f'attachment; filename="statistical_map.nii.gz"'
    }

    full_filename = func(parcellation_id, region_id, space_id)
    assert os.path.isfile(full_filename), f"file saved incorrectly"
    return FileResponse(full_filename, headers=headers)

class StatisticModelInfo(BaseModel):
    min: float
    max: float

@router.get("/statistical_map.info.json", response_model=StatisticModelInfo, tags=TAGS)
@version(*FASTAPI_VERSION)
@router_decorator(ROLE, func=get_region_statistic_map_info)
def route_get_region_statistical_map(parcellation_id: str, space_id: str, region_id: str, *, func):
    if func is None:
        raise HTTPException(500, f"func: None passsed")
    
    data = func(parcellation_id, region_id, space_id)
    return StatisticModelInfo(**data)
