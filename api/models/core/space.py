from pydantic import Field
from typing import List, Dict


from api.models._commons import ConfigBaseModel
from api.models.openminds.SANDS.v3.atlas.commonCoordinateSpace import (
    Model as _CommonCoordinateSpaceModel,
    AxesOrigin,
)
from api.models.openminds.SANDS.v3.miscellaneous.coordinatePoint import (
    Model as _CoordinatePointModel,
    Coordinates as QuantitativeValueModel,
)

class CommonCoordinateSpaceModel(_CommonCoordinateSpaceModel, ConfigBaseModel, type="core/space"): pass

class CoordinatePointModel(_CoordinatePointModel, ConfigBaseModel, type="core/space/point"): pass

class LocationModel(ConfigBaseModel, type="core/space/location"):
    id: str = Field(..., alias="@id")
    type: str = Field(..., alias="@type")
    space: Dict[str, str]

class BoundingBoxModel(LocationModel, type="core/space/bbox"):
    center: CoordinatePointModel
    minpoint: CoordinatePointModel
    maxpoint: CoordinatePointModel
    shape: List[float]
    is_planar: bool = Field(..., alias="isPlanar")
