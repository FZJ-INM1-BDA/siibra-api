from pydantic import Field
from new_api.v3.models._commons import (
    ConfigBaseModel,
)
from new_api.v3.models._retrieval.datasets import EbrainsDatasetModel
from typing import Optional, List, Any
from abc import ABC

class SiibraPublication(ConfigBaseModel):
    citation: str
    url: str

class _SiibraAtlasConcept(ConfigBaseModel, ABC):
    id: str = Field(..., alias="@id")
    name: str
    shortname: Optional[str]
    modality: Optional[str]
    description: Optional[str]
    publications: List[SiibraPublication]
    datasets: List[EbrainsDatasetModel]

class SiibraAtlasConcept(_SiibraAtlasConcept):
    """SiibraAtlasConcept"""
    pass
