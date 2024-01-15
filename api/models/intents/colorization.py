from typing import List
from pydantic import BaseModel

from .base import _BaseIntent

from ..core.region import ParcellationEntityVersionModel

class RegionMapping(BaseModel):
    region: ParcellationEntityVersionModel
    rgb: List[int]

class ColorizationIntent(_BaseIntent, type="colorization"):
    region_mappings: List[RegionMapping]

