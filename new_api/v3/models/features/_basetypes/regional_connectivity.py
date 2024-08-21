from typing import Optional, Dict, List
from new_api.v3.models.features._basetypes.feature import _FeatureModel
from new_api.v3.models._commons import DataFrameModel

class SiibraRegionalConnectivityModel(_FeatureModel, type="regional_connectivity"):
    """SiibraRegionalConnectivityModel"""
    cohort: str
    subjects: List[str]
    matrices: Optional[Dict[str, DataFrameModel]]
