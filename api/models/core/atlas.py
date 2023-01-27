from pydantic import Field
from typing import List
from api.models.openminds.controlledTerms.v1.species import Model as _SpeciesModel
from api.models._commons import (
    SiibraAtIdModel,
    ConfigBaseModel,
)

class SpeciesModel(_SpeciesModel):
    kg_v1_id: str = Field(..., alias="kgV1Id")

class SiibraAtlasModel(ConfigBaseModel, type="core/atlas"):
    id: str = Field(..., alias="@id")
    name: str
    spaces: List[SiibraAtIdModel]
    parcellations: List[SiibraAtIdModel]
    species: str
