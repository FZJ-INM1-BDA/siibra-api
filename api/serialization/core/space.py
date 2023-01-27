from api.models.core.space import (
    LocationModel,
    QuantitativeValueModel,
    CoordinatePointModel,
    BoundingBoxModel,
    CommonCoordinateSpaceModel,
    AxesOrigin,
)
from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import Space, BoundingBox, Point
from datetime import date

@serialize(Space)
def space_to_model(spc: Space, **kwargs) -> CommonCoordinateSpaceModel:
    return CommonCoordinateSpaceModel(
        id=spc.id,
        anatomical_axes_orientation={
            "@id": "https://openminds.ebrains.eu/vocab/anatomicalAxesOrientation/XYZ"
        },
        axes_origin=[
            AxesOrigin(value=0),
            AxesOrigin(value=0),
            AxesOrigin(value=0),
        ],
        default_image=[instance_to_model(vol) for vol in spc.volumes],
        full_name=spc.name,
        native_unit={
            "@id": "https://openminds.ebrains.eu/controlledTerms/Terminology/unitOfMeasurement/um"
        },
        release_date=str(date(2015, 1, 1)),
        short_name=spc.name,
        version_identifier=spc.name,
    )

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


@serialize(BoundingBox, pass_super_model=True)
def boundingbox_to_model(bbox: BoundingBox, super_model_dict={}, **kwargs) -> BoundingBoxModel:
    return BoundingBoxModel(
        **super_model_dict,
        id=bbox.id,
        center=instance_to_model(bbox.center, **kwargs),
        minpoint=instance_to_model(bbox.minpoint, **kwargs),
        maxpoint=instance_to_model(bbox.maxpoint, **kwargs),
        shape=bbox.shape,
        is_planar=bbox.is_planar,
    )
