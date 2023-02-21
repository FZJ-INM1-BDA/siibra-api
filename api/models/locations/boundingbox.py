from .point import CoordinatePointModel
from .location import _LocationModel
from typing import List
from pydantic import Field

class BoundingBoxModel(_LocationModel, type="bbox"):
    center: CoordinatePointModel
    minpoint: CoordinatePointModel
    maxpoint: CoordinatePointModel
    shape: List[float]
    is_planar: bool = Field(..., alias="isPlanar")
