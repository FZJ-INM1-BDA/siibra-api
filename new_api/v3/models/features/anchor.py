from typing import Optional, List, Union
from new_api.v3.models._commons import ConfigBaseModel
from new_api.v3.models.locations.location import LocationModel
from new_api.v3.models.locations.point import (
    CoordinatePointModel,
)
from new_api.v3.models.core.region import ParcellationEntityVersionModel
from new_api.v3.models.core.parcellation import SiibraParcellationModel
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
    query_structure: Union[LocationModel, ParcellationEntityVersionModel, SiibraParcellationModel]
    assigned_structure: Union[LocationModel, ParcellationEntityVersionModel, SiibraParcellationModel]
    explanation: str


class SiibraAnchorModel(ConfigBaseModel, type="anchor"):
    """SiibraAnchorModel"""
    location: Optional[Union[LocationModel, CoordinatePointModel]]
    regions: List[SiibraRegionAssignmentQual]
    last_match_description: str=""
    last_match_result: List[SiibraAnatomicalAssignmentModel]=Field(default_factory=list)
