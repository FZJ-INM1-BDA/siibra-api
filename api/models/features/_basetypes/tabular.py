from api.models.features._basetypes.feature import FeatureModel
from api.models._commons import DataFrameModel
from typing import Optional

class SiibraTabularModel(FeatureModel, type="features/_basetype/tabular"):
    data: Optional[DataFrameModel]
