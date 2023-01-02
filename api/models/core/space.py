from pydantic import Field
from typing import List, Dict


from api.models.openminds.base import ConfigBaseModel
from api.models.openminds.SANDS.v3.atlas import commonCoordinateSpace
from api.models.openminds.SANDS.v3.miscellaneous.coordinatePoint import (
    Model as CoordinatePointModel,
    Coordinates as QuantitativeValueModel,
)

class LocationModel(ConfigBaseModel):
    id: str = Field(..., alias="@id")
    type: str = Field(..., alias="@type")
    space: Dict[str, str]

class BoundingBoxModel(LocationModel):
    center: CoordinatePointModel
    minpoint: CoordinatePointModel
    maxpoint: CoordinatePointModel
    shape: List[float]
    is_planar: bool = Field(..., alias="isPlanar")
