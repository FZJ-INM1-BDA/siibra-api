from typing import Optional, Dict, List
from api.models.features._basetypes.feature import FeatureModel
from api.models._commons import DataFrameModel

class SiibraRegionalConnectivityModel(FeatureModel, type="regional_connectivity"):
    cohort: str
    subjects: List[str]
    matrices: Optional[Dict[str, DataFrameModel]]
