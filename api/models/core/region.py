from api.models.openminds.SANDS.v3.atlas.parcellationEntityVersion import (
    Model as ParcellationEntityVersionModel,
    Coordinates,
    BestViewPoint,
    HasAnnotation,
)
from api.models.openminds.SANDS.v3.atlas.parcellationEntity import (
    Model as ParcellationEntityModel,
)

OPENMINDS_PARCELLATION_ENTITY_VERSION_TYPE = (
    "https://openminds.ebrains.eu/sands/ParcellationEntityVersion"
)

class UnitOfMeasurement:
    MILLIMETER = "https://openminds.ebrains.eu/instances/unitOfMeasurement/millimeter"
