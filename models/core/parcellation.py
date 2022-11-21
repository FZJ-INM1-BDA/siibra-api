from models.openminds.base import SiibraAtIdModel, ConfigBaseModel
from models.openminds.SANDS.v3.atlas.brainAtlasVersion import (
    Model as BrainAtlasVersionModel,
    HasTerminologyVersion,
)

from typing import Optional, List
from pydantic import Field


SIIBRA_PARCELLATION_MODEL_TYPE = "minds/core/parcellationatlas/v1.0.0"
BRAIN_ATLAS_VERSION_TYPE = "https://openminds.ebrains.eu/sands/BrainAtlasVersion"


class AtlasType:
    DETERMINISTIC_ATLAS = "https://openminds.ebrains.eu/instances/atlasType/deterministicAtlas"
    PARCELLATION_SCHEME = "https://openminds.ebrains.eu/instances/atlasType/parcellationScheme"
    PROBABILISTIC_ATLAS = "https://openminds.ebrains.eu/instances/atlasType/probabilisticAtlas"


class SiibraParcellationVersionModel(ConfigBaseModel):
    name: str
    deprecated: Optional[bool]
    prev: Optional[SiibraAtIdModel]
    next: Optional[SiibraAtIdModel]


class SiibraParcellationModel(ConfigBaseModel):
    id: str = Field(..., alias="@id")
    type: str = Field(SIIBRA_PARCELLATION_MODEL_TYPE, const=True, alias="@type")
    name: str
    modality: Optional[str]
    brain_atlas_versions: List[BrainAtlasVersionModel] = Field(..., alias="brainAtlasVersions")
    version: Optional[SiibraParcellationVersionModel]
