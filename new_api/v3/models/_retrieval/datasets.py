from pydantic import Field
from new_api.v3.models._commons import (
    ConfigBaseModel,
)
from typing import List, Optional

class EbrainsDsUrl(ConfigBaseModel):
    """EbrainsDsUrl"""
    url: str

class EbrainsDsPerson(ConfigBaseModel):
    """EbrainsDsPerson"""
    id: str = Field(..., alias="@id")
    schema_shortname: Optional[str] = Field(None, alias="schema.org/shortName")
    identifier: str
    shortName: str
    name: str

class EbrainsDatasetModel(ConfigBaseModel):
    """EbrainsDatasetModel"""
    id: str = Field(..., alias="@id")
    name: str
    urls: List[EbrainsDsUrl]
    description: Optional[str]
    contributors: List[EbrainsDsPerson]
    ebrains_page: Optional[str]
    custodians:  List[EbrainsDsPerson]
