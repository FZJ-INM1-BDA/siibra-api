from new_api.v3.models._commons import SiibraAtIdModel, ConfigBaseModel
from new_api.v3.models.openminds.SANDS.v3.atlas.brainAtlasVersion import (
    Model as _BrainAtlasVersionModel,
    HasTerminologyVersion,
)
from new_api.v3.models._retrieval.datasets import EbrainsDatasetModel

from typing import Optional, List
from pydantic import Field

class BrainAtlasVersionModel(_BrainAtlasVersionModel, ConfigBaseModel, type="parcellation_bav"): pass

class AtlasType:
    DETERMINISTIC_ATLAS = "https://openminds.ebrains.eu/instances/atlasType/deterministicAtlas"
    PARCELLATION_SCHEME = "https://openminds.ebrains.eu/instances/atlasType/parcellationScheme"
    PROBABILISTIC_ATLAS = "https://openminds.ebrains.eu/instances/atlasType/probabilisticAtlas"


class SiibraParcellationVersionModel(ConfigBaseModel, type="parcellation_version"):
    """SiibraParcellationVersionModel"""
    name: str
    deprecated: Optional[bool]
    prev: Optional[SiibraAtIdModel]
    next: Optional[SiibraAtIdModel]


class SiibraParcellationModel(ConfigBaseModel, type="parcellation"):
    """SiibraParcellationModel"""
    id: str = Field(..., alias="@id")
    type: str = Field(..., alias="@type")
    name: str
    modality: Optional[str]
    datasets: List[EbrainsDatasetModel]
    brain_atlas_versions: List[BrainAtlasVersionModel] = Field(..., alias="brainAtlasVersions")
    version: Optional[SiibraParcellationVersionModel]
    shortname: Optional[str]

