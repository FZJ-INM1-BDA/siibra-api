from datetime import date
from pydantic import Field
from typing import List, Optional

from siibra.core.space import Space, Point, BoundingBox, Location

from app.models.util import serialize
from app.models.openminds.base import ConfigBaseModel
from app.models.core.datasets import DatasetJsonModel

class CorticalCellModel(ConfigBaseModel):
    x: float
    y: float
    area: float
    layer: int
    instance_label: int = Field(..., alias="instance label")


class CorticalCellDistributionModel(DatasetJsonModel):
    id: str = Field(..., alias="@id")
    type: str = Field("siibra/features/cells", const=True, alias="@type")
    cells: Optional[List[CorticalCellModel]]
    section: Optional[str]
    patch: Optional[str]
