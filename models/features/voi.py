from models.core.datasets import DatasetJsonModel
from models.core.space import BoundingBoxModel
from models.volumes.volume import VolumeModel
from pydantic import Field
from typing import List

class VOIDataModel(DatasetJsonModel):
    type: str = Field("siibra/features/voi", const=True, alias="@type")
    volumes: List[VolumeModel]
    location: BoundingBoxModel
