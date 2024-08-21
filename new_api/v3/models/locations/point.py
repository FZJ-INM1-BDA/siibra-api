from new_api.v3.models.openminds.SANDS.v3.miscellaneous.coordinatePoint import (
    Model as _CoordinatePointModel,
    Coordinates as QuantitativeValueModel,
)
from new_api.v3.models._commons import ConfigBaseModel

class CoordinatePointModel(_CoordinatePointModel, ConfigBaseModel, type="point"):
    """CoordinatePointModel"""
    pass
