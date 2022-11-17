from pydantic import Field
from typing import List
from models.openminds.controlledTerms.v1.species import Model as _SpeciesModel
from models.openminds.base import (
    SiibraAtIdModel,
    ConfigBaseModel,
)

class SpeciesModel(_SpeciesModel):
    kg_v1_id: str = Field(..., alias="kgV1Id")

class SiibraAtlasModel(ConfigBaseModel):
    id: str = Field(..., alias="@id")
    name: str
    type: str = Field("juelich/iav/atlas/v1.0.0", const=True, alias="@type")
    spaces: List[SiibraAtIdModel]
    parcellations: List[SiibraAtIdModel]
    species: SpeciesModel
