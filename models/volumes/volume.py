from typing import Optional, Dict, Any
from pydantic import Field
from models.openminds.base import (
    ConfigBaseModel,
    SiibraAtIdModel,
)
from models.core.datasets import DatasetJsonModel

class VolumeDataModel(ConfigBaseModel):
    type: str
    is_volume: bool
    is_surface: bool
    detail: Dict[str, Any]
    space: SiibraAtIdModel
    url: Optional[str]
    url_map: Optional[Dict[str, str]]
    map_type: Optional[str]
    volume_type: Optional[str]


class VolumeModel(DatasetJsonModel):
    type: str = Field(..., alias="@type")
    data: VolumeDataModel
