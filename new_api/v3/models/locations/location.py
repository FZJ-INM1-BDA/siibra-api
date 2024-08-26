from new_api.v3.models._commons import ConfigBaseModel, SiibraAtIdModel
from pydantic import Field
from abc import ABC

class _LocationModel(ConfigBaseModel, ABC, type="location"):
    """Location, as specified by space.[@id]. Unit of measurement is mm, unless specified otherwise."""

    type: str = Field(..., alias="@type")
    space: SiibraAtIdModel = Field(..., description="Space (id) by which the location is found. More detail of the space can be found by querying /v3_0/spaces/{space_id}")

class LocationModel(_LocationModel):
    """LocationModel"""
    pass
