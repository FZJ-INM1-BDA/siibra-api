from api.models.features._basetypes.feature import _FeatureModel
from api.models._commons import DataFrameModel
from typing import Optional
from abc import ABC

class _SiibraTabularModel(_FeatureModel, ABC, type="tabular"):
    """AbstractBaseModel
    
    see [api.models._commons.ConfigBaseModel][]"""
    data: Optional[DataFrameModel]

class SiibraTabularModel(_SiibraTabularModel):
    """SiibraTabularModel"""
    pass
