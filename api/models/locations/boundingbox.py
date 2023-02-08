from .point import CoordinatePointModel
from .location import LocationModel
from typing import List
from pydantic import Field

class BoundingBoxModel(LocationModel, type="core/space/bbox"):
    center: CoordinatePointModel
    minpoint: CoordinatePointModel
    maxpoint: CoordinatePointModel
    shape: List[float]
    is_planar: bool = Field(..., alias="isPlanar")
