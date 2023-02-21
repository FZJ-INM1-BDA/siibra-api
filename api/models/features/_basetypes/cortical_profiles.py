from typing import Optional, Dict
from api.models.features._basetypes.feature import _FeatureModel
from api.models._commons import SeriesModel

class SiibraCorticalProfileModel(_FeatureModel, type="cortical_profile"):
    unit: Optional[str]
    boundary_positions: Dict[str, float]
    boundaries_mapped: bool
    data: Optional[SeriesModel]
