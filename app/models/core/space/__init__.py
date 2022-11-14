from datetime import date
from pydantic import Field
from typing import List, Dict
from siibra.core.space import Space, Point, BoundingBox, Location
from app.models.util import serialize

from app.models.openminds.base import ConfigBaseModel
from app.models.openminds.SANDS.v3.atlas import commonCoordinateSpace
from app.models.openminds.SANDS.v3.miscellaneous.coordinatePoint import (
    Model as CoordinatePointModel,
    Coordinates as QuantitativeValueModel,
)

@serialize(Space)
def space_to_model(spc: Space, **kwargs) -> commonCoordinateSpace.Model:
    return commonCoordinateSpace.Model(
        id=spc.id,
        type="https://openminds.ebrains.eu/sands/CoordinateSpace",
        anatomical_axes_orientation={
            "@id": "https://openminds.ebrains.eu/vocab/anatomicalAxesOrientation/XYZ"
        },
        axes_origin=[
            commonCoordinateSpace.AxesOrigin(value=0),
            commonCoordinateSpace.AxesOrigin(value=0),
            commonCoordinateSpace.AxesOrigin(value=0),
        ],
        default_image=[{"@id": vol.id} for vol in spc.volumes],
        full_name=spc.name,
        native_unit={
            "@id": "https://openminds.ebrains.eu/controlledTerms/Terminology/unitOfMeasurement/um"
        },
        release_date=date(2015, 1, 1),
        short_name=spc.name,
        version_identifier=spc.name,
    )


class LocationModel(ConfigBaseModel):
    id: str = Field(..., alias="@id")
    type: str = Field(..., alias="@type")
    space: Dict[str, str]

@serialize(Location)
def location_to_model(location: Location, **kwargs) -> LocationModel:
    return LocationModel(
        id=f"spy/location/space:{location.space.id if location.space is not None else 'None'}",
        space={"@id": location.space.id},
        type="spy/location",
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
        type="https://openminds.ebrains.eu/sands/CoordinatePoint",
        coordinate_space={"@id": space_id},
        coordinates=[QuantitativeValueModel(value=coord) for coord in point],
    )


class BoundingBoxModel(LocationModel):
    center: CoordinatePointModel
    minpoint: CoordinatePointModel
    maxpoint: CoordinatePointModel
    shape: List[float]
    is_planar: bool = Field(..., alias="isPlanar")

@serialize(BoundingBox)
def boundingbox_to_model(bbox: BoundingBox, **kwargs) -> BoundingBoxModel:
    from app.models import instance_to_model
    super_model = instance_to_model(bbox, **kwargs)
    return BoundingBoxModel(
        **super_model.dict(),
        id=bbox.id,
        center=instance_to_model(bbox.center, **kwargs),
        minpoint=instance_to_model(bbox.minpoint, **kwargs),
        maxpoint=instance_to_model(bbox.maxpoint, **kwargs),
        shape=bbox.shape,
        is_planar=bbox.is_planar,
    )
