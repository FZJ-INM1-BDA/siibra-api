from api.models.locations.point import (
    CoordinatePointModel,
    QuantitativeValueModel,
)
from api.serialization.util.siibra import Space, BoundingBox, Point
from api.serialization.util import serialize, instance_to_model

# Point is a special case, since the model does not directly derive from SiibraLocationModel, but an entity that exists on OpenMinds
@serialize(Point)
def point_to_model(point: Point, **kwargs) -> CoordinatePointModel:
    if point.space is None:
        raise RuntimeError(
            "Point.to_model cannot be done on Location entity that does not have space defined!"
        )
    space_id = point.space.id

    return CoordinatePointModel(
        id=point.id,
        coordinate_space={"@id": space_id},
        coordinates=[QuantitativeValueModel(value=coord) for coord in point],
    )
