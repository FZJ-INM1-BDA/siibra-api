from api.models._commons import ConfigBaseModel
from api.models._retrieval.datasets import EbrainsDatasetModel
from api.models.features.anchor import SiibraAnchorModel
from typing import List

class FeatureModel(ConfigBaseModel, type="features/_basetypes/feature"):
    id: str
    modality: str
    description: str
    name: str
    datasets: List[EbrainsDatasetModel]
    anchor: SiibraAnchorModel
