from api.models.openminds.base import ConfigBaseModel
from typing import Optional, Dict


class FeatureModel(ConfigBaseModel): ...


class RegionalFeatureModel(FeatureModel):...


class FPDataModel(ConfigBaseModel):
    mean: Dict[str, float]
    std: Dict[str, float]


class RegionalFingerprintModel(RegionalFeatureModel):
    description: str
    measuretype: str
    unit: Optional[str]
    data: Optional[FPDataModel]
    name: str

class CorticalProfileModel(RegionalFeatureModel):
    measuretype: str
    description: str
    unit: str
    name: str
    data: Optional[Dict[str, float]]
