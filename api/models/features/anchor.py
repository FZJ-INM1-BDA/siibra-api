from typing import Optional, List, Union
from api.models._commons import ConfigBaseModel
from api.models.locations.location import LocationModel
from api.models.locations.point import (
    CoordinatePointModel,
)
from api.models.core.region import ParcellationEntityVersionModel
from pydantic import Field

class SiibraRegionAssignmentQual(ConfigBaseModel):
    """
    SiibraRegionAssignmentModel
    """
    region: ParcellationEntityVersionModel
    qualification: str


class SiibraAnatomicalAssignmentModel(ConfigBaseModel, type="anatomical_assignment"):
    """SiibraAnatomicalAssignmentModel"""
    qualification: str
    query_structure: Union[LocationModel, ParcellationEntityVersionModel]
    assigned_structure: Union[LocationModel, ParcellationEntityVersionModel]
    explanation: str


class SiibraAnchorModel(ConfigBaseModel, type="anchor"):
    """SiibraAnchorModel"""
    location: Optional[Union[LocationModel, CoordinatePointModel]]
    regions: List[SiibraRegionAssignmentQual]
    last_match_description: str=""
    last_match_result: List[SiibraAnatomicalAssignmentModel]=Field(default_factory=list)
