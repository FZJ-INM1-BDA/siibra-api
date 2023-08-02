from api.models._commons import ConfigBaseModel, SiibraAtIdModel
from pydantic import Field
from abc import ABC

class _LocationModel(ConfigBaseModel, ABC, type="location"):
    type: str = Field(..., alias="@type")
    space: SiibraAtIdModel

class LocationModel(_LocationModel):
    """LocationModel"""
    pass
