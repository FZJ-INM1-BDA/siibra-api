from typing import Optional, List, Union
from api.models._commons import ConfigBaseModel
from api.models.locations.location import LocationModel
from api.models.locations.point import (
    CoordinatePointModel,
)
from api.models.core.region import ParcellationEntityVersionModel

class SiibraRegionAssignmentQual(ConfigBaseModel):
    region: ParcellationEntityVersionModel
    qualification: str

class SiibraAnchorModel(ConfigBaseModel, type="anchor"):
    location: Optional[Union[LocationModel, CoordinatePointModel]]
    regions: List[SiibraRegionAssignmentQual]
