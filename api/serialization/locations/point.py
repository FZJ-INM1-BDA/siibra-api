from api.models.locations.point import (
    CoordinatePointModel,
    QuantitativeValueModel,
)
from api.serialization.util.siibra import Space, BoundingBox, Point
from api.serialization.util import serialize, instance_to_model
from api.common.exceptions import InvalidParameters

# Point is a special case, since the model does not directly derive from SiibraLocationModel, but an entity that exists on OpenMinds
@serialize(Point)
def point_to_model(point: Point, **kwargs) -> CoordinatePointModel:
    """Serialization of Point instance
    
    Args:
        point: Point instance to be serialized
    
    Returns:
        CoordinatePointModel
    
    Raises:
        InvalidParameters: if point does not have space defined"""
    if point.space is None:
        raise InvalidParameters(
            "Point.to_model cannot be done on Location entity that does not have space defined!"
        )
    space_id = point.space.id

    return CoordinatePointModel(
        id=point.id,
        coordinate_space={"@id": space_id},
        coordinates=[QuantitativeValueModel(value=coord) for coord in point],
    )
