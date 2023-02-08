from api.models._commons import ConfigBaseModel, SiibraAtIdModel
from pydantic import Field

class LocationModel(ConfigBaseModel, type="location"):
    type: str = Field(..., alias="@type")
    space: SiibraAtIdModel
