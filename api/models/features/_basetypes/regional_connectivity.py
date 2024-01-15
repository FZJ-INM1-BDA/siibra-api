from typing import Optional, Dict, List
from api.models.features._basetypes.feature import _FeatureModel
from api.models._commons import DataFrameModel

class SiibraRegionalConnectivityModel(_FeatureModel, type="regional_connectivity"):
    """SiibraRegionalConnectivityModel"""
    cohort: str
    subject: str
    feature: Optional[str]
    matrix: Optional[DataFrameModel]
