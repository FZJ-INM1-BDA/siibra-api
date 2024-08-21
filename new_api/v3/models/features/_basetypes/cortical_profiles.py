from typing import Optional, Dict
from new_api.v3.models.features._basetypes.tabular import _SiibraTabularModel

class SiibraCorticalProfileModel(_SiibraTabularModel, type="cortical_profile"):
    """SiibraCorticalProfileModel"""
    unit: Optional[str]
    boundary_positions: Dict[str, float]
    boundaries_mapped: bool
