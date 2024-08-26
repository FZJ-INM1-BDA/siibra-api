from .point import CoordinatePointModel
from .location import _LocationModel
from typing import List
from pydantic import Field

class BoundingBoxModel(_LocationModel, type="bbox"):
    """BoundingBoxModel. Describes an axis aligned boundingbox. As a result, only the most left-posterior-inferior and most right-anterior-superior points are needed to define all eight vertices of the bounding box."""
    center: CoordinatePointModel = Field(..., description="Center point of the bounding box")
    minpoint: CoordinatePointModel = Field(..., description="Most left-posterior-inferior point of the bounding box")
    maxpoint: CoordinatePointModel = Field(..., description="Most right-anterior-superior point of the bounding box")
    shape: List[float]
    is_planar: bool = Field(..., alias="isPlanar")
