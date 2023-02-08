from typing import Optional, Dict, List
from api.models.features._basetypes.feature import FeatureModel
from api.models.volumes.volume import VolumeModel
from api.models._commons import SiibraAtIdModel, ConfigBaseModel
from api.models.locations.location import LocationModel
from api.models.core.region import ParcellationEntityModel

class SiibraRegionAssignmentQual(ConfigBaseModel):
    region: ParcellationEntityModel
    qualification: str

class SiibraAnchorModel(FeatureModel, type="features/anchor"):
    location: Optional[LocationModel]
    regions: List[SiibraRegionAssignmentQual]
