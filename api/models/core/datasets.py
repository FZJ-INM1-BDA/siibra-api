from pydantic import Field
from typing import List, Optional
from api.models._commons import ConfigBaseModel
from api.models.openminds.core.v4.products.datasetVersion import(
    Model as DatasetVersionModel
)

DATASET_TYPE = "https://openminds.ebrains.eu/core/DatasetVersion"

class Url(ConfigBaseModel):
    doi: str
    cite: Optional[str]

class DatasetJsonModel(ConfigBaseModel):
    id: str = Field(..., alias="@id")
    type: str = Field(DATASET_TYPE, alias="@type", const=True)
    metadata: DatasetVersionModel
    urls: List[Url]
