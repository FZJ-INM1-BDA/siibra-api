from api.models.openminds.SANDS.v3.miscellaneous.coordinatePoint import (
    Model as _CoordinatePointModel,
    Coordinates as QuantitativeValueModel,
)
from api.models._commons import ConfigBaseModel

class CoordinatePointModel(_CoordinatePointModel, ConfigBaseModel, type="point"): pass
