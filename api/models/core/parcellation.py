from api.models._commons import SiibraAtIdModel, ConfigBaseModel
from api.models.openminds.SANDS.v3.atlas.brainAtlasVersion import (
    Model as _BrainAtlasVersionModel,
    HasTerminologyVersion,
)

from typing import Optional, List
from pydantic import Field

class BrainAtlasVersionModel(_BrainAtlasVersionModel, ConfigBaseModel, type="core/parcellation/bav"): pass

class AtlasType:
    DETERMINISTIC_ATLAS = "https://openminds.ebrains.eu/instances/atlasType/deterministicAtlas"
    PARCELLATION_SCHEME = "https://openminds.ebrains.eu/instances/atlasType/parcellationScheme"
    PROBABILISTIC_ATLAS = "https://openminds.ebrains.eu/instances/atlasType/probabilisticAtlas"


class SiibraParcellationVersionModel(ConfigBaseModel, type="core/parcellation/version"):
    name: str
    deprecated: Optional[bool]
    prev: Optional[SiibraAtIdModel]
    next: Optional[SiibraAtIdModel]


class SiibraParcellationModel(ConfigBaseModel, type="core/parcellation"):
    id: str = Field(..., alias="@id")
    type: str = Field(..., alias="@type")
    name: str
    modality: Optional[str]
    brain_atlas_versions: List[BrainAtlasVersionModel] = Field(..., alias="brainAtlasVersions")
    version: Optional[SiibraParcellationVersionModel]
