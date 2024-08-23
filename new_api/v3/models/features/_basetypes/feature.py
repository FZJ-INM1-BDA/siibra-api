from new_api.v3.models._commons import ConfigBaseModel
from new_api.v3.models._retrieval.datasets import EbrainsDatasetModel
from new_api.v3.models.features.anchor import SiibraAnchorModel
from typing import List, Optional
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