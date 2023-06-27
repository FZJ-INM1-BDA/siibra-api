from pydantic import Field
from api.models._commons import (
    ConfigBaseModel,
)
from typing import List, Union, Optional

class EbrainsDsUrl(ConfigBaseModel):
    url: str

class EbrainsDsPerson(ConfigBaseModel):
    id: str = Field(..., alias="@id")
    schema_shortname: Optional[str] = Field(..., alias="schema.org/shortName")
    identifier: str
    shortName: str
    name: str

class EbrainsDsEmbargoStatus(ConfigBaseModel):
    id: str = Field(..., alias="@id")
    name: str
    identifier: Union[List[str], str]

class EbrainsDatasetModel(ConfigBaseModel):
    id: str = Field(..., alias="@id")
    name: str
    urls: List[EbrainsDsUrl]
    description: Optional[str]
    contributors: List[EbrainsDsPerson]
    ebrains_page: Optional[str]
    custodians:  List[EbrainsDsPerson]
