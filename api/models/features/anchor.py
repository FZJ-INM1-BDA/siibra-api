from typing import Optional, List
from api.models._commons import ConfigBaseModel
from api.models.locations.location import LocationModel
from api.models.core.region import ParcellationEntityVersionModel

class SiibraRegionAssignmentQual(ConfigBaseModel):
    region: ParcellationEntityVersionModel
    qualification: str

class SiibraAnchorModel(ConfigBaseModel, type="anchor"):
    location: Optional[LocationModel]
    regions: List[SiibraRegionAssignmentQual]
