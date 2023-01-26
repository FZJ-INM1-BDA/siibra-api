from pydantic import Field
from api.models._commons import (
    ConfigBaseModel,
)
from api.models._retrieval.datasets import EbrainsDatasetModel
from typing import Optional, List, Any

class SiibraPublication(ConfigBaseModel):
    citation: str
    url: str

class SiibraAtlasConcept(ConfigBaseModel):
    id: str = Field(..., alias="@id")
    name: str
    shortname: Optional[str]
    modality: Optional[str]
    description: Optional[str]
    publications: List[SiibraPublication]
    datasets: List[EbrainsDatasetModel]
