from api.models._commons import ConfigBaseModel
from api.models._retrieval.datasets import EbrainsDatasetModel
from api.models.features.anchor import SiibraAnchorModel
from typing import List, Optional

class FeatureModel(ConfigBaseModel, type="feature"):
    id: str
    modality: str
    description: str
    name: str
    datasets: List[EbrainsDatasetModel]
    anchor: Optional[SiibraAnchorModel]
