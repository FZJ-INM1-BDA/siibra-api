from pydantic import Field
from typing import Optional, List, Dict
from models.openminds.base import ConfigBaseModel
from models.util import NpArrayDataModel


class ConnectivityMatrixDataModel(ConfigBaseModel):
    id: str = Field(..., alias="@id")
    type: str = Field(..., alias="@type")
    name: Optional[str]
    description: Optional[str]
    citation: Optional[str]
    authors: Optional[List[str]]
    cohort: Optional[str]
    subject: Optional[str]

    filename: Optional[str]
    dataset_id: Optional[str]

    parcellations: List[Dict[str, str]]
    matrix: Optional[NpArrayDataModel]
    columns: Optional[List[str]]

