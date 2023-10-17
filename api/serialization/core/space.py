from api.models.core.space import (
    CommonCoordinateSpaceModel,
    AxesOrigin,
)
from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import Space, BoundingBox, Point
from datetime import date

@serialize(Space)
def space_to_model(space: Space, **kwargs) -> CommonCoordinateSpaceModel:
    """Serialize space object into CommonCoordinateSpaceModel
    
    Args:
        space: space object to be serialized
        
    Returns:
        CommonCoordinateSpaceModel"""
    return CommonCoordinateSpaceModel(
        id=space.id,
        anatomical_axes_orientation={
            "@id": "https://openminds.ebrains.eu/vocab/anatomicalAxesOrientation/XYZ"
        },
        axes_origin=[
            AxesOrigin(value=0),
            AxesOrigin(value=0),
            AxesOrigin(value=0),
        ],
        default_image=[instance_to_model(vol) for vol in space.volumes],
        full_name=space.name,
        native_unit={
            "@id": "https://openminds.ebrains.eu/controlledTerms/Terminology/unitOfMeasurement/um"
        },
        release_date=str(date(2015, 1, 1)),
        short_name=space.shortname,
        version_identifier=space.name,
        datasets=[instance_to_model(ds) for ds in (space.datasets or [])]
    )
