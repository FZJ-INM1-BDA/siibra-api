from api.models._commons import ConfigBaseModel
from api.models._retrieval.datasets import EbrainsDatasetModel
from api.models.features.anchor import SiibraAnchorModel
from api.models.locations.point import CoordinatePointModel
from typing import List, Optional, Union
from abc import ABC

class _FeatureModel(ConfigBaseModel, ABC, type="feature"):
    """AbstractBaseModel
    
    see [api.models._commons.ConfigBaseModel][]"""
    
    id: str
    modality: Optional[str] # ebrains dataset do not have modality populated
    category: str
    description: str
    name: str
    datasets: List[EbrainsDatasetModel]
    anchor: Optional[SiibraAnchorModel]

class FeatureModel(_FeatureModel):
    """FeatureModel"""
    pass

class SubfeatureModel(ConfigBaseModel):
    id: str
    index: Union[str, CoordinatePointModel]
    name: str

class CompoundFeatureModel(_FeatureModel, type="compoundfeature"):
    indices: List[SubfeatureModel]
