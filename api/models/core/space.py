from api.models._commons import ConfigBaseModel
from api.models.openminds.SANDS.v3.atlas.commonCoordinateSpace import (
    Model as _CommonCoordinateSpaceModel,
    AxesOrigin,
)

class CommonCoordinateSpaceModel(_CommonCoordinateSpaceModel, ConfigBaseModel, type="core/space"): pass
