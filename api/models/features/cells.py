from api.models.openminds.base import ConfigBaseModel
from api.models.core.datasets import DatasetJsonModel
from pydantic import Field
from typing import List, Optional

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
