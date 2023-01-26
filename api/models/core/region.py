from api.models.openminds.SANDS.v3.atlas.parcellationEntityVersion import (
    Model as _ParcellationEntityVersionModel,
    Coordinates,
    BestViewPoint,
    HasAnnotation,
)
from api.models.openminds.SANDS.v3.atlas.parcellationEntity import (
    Model as ParcellationEntityModel,
)
from api.models._commons import ConfigBaseModel

class ParcellationEntityVersionModel(_ParcellationEntityVersionModel, ConfigBaseModel, type="core/region"):pass

class UnitOfMeasurement:
    MILLIMETER = "https://openminds.ebrains.eu/instances/unitOfMeasurement/millimeter"
