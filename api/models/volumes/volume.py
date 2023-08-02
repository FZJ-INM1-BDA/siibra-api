from typing import Optional, Dict, Any, List, Union
from pydantic import Field
from enum import Enum
from api.models._commons import (
    ConfigBaseModel,
    SiibraAtIdModel,
)
from api.models._retrieval.datasets import EbrainsDatasetModel

class VolumeModel(ConfigBaseModel):
    """VolumeModel"""
    name: str
    formats: List[str]
    
    provides_mesh: bool = Field(..., alias="providesMesh")
    provides_image: bool = Field(..., alias="providesImage")

    fragments: Dict[str, List[str]]
    variant: Optional[str]

    provided_volumes: Dict[str, Union[str, Dict[str, str]]] = Field(..., alias="providedVolumes")

    space: SiibraAtIdModel

    datasets: List[EbrainsDatasetModel]


class MapType(str, Enum):
    """MapType
    
    Exact match to MapType in siibra, to avoid dependency on siibra"""
    LABELLED = "LABELLED"
    STATISTICAL = "STATISTICAL"
