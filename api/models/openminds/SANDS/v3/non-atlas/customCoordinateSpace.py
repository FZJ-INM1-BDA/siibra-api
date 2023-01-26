# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/SANDS/v3/non-atlas/customCoordinateSpace.schema.json

from typing import Any, Dict, List, Optional

from pydantic import Field
from api.models.openminds.base import SiibraBaseModel


class AxesOrigin(SiibraBaseModel):
    type_of_uncertainty: Optional[Any] = Field(
        None,
        alias='typeOfUncertainty',
        description='Distinct technique used to quantify the uncertainty of a measurement.',
        title='typeOfUncertainty',
    )
    uncertainty: Optional[List[float]] = Field(
        None,
        description='Quantitative value range defining the uncertainty of a measurement.',
        max_items=2,
        min_items=2,
        title='uncertainty',
    )
    unit: Optional[Any] = Field(
        None,
        description='Determinate quantity adopted as a standard of measurement.',
        title='unit',
    )
    value: float = Field(..., description='Entry for a property.', title='value')


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    anatomical_axes_orientation: Dict[
        str, Any
    ] = Field(
        ...,
        alias='anatomicalAxesOrientation',
        description='Relation between reference planes used in anatomy and mathematics.',
        title='anatomicalAxesOrientation',
    )
    axes_origin: 'AxesOrigin' = Field(
        ...,
        alias='axesOrigin',
        description='Structured information on a quantitative value.',
    )
    default_image: Optional[List[Any]] = Field(
        None,
        alias='defaultImage',
        description='Two or three dimensional image that particluarly represents a specific coordinate space.',
        min_items=1,
        title='defaultImage',
    )
    name: str = Field(
        ...,
        alias='name',
        description='Word or phrase that constitutes the distinctive designation of a being or thing.',
        title='name',
    )
    native_unit: Dict[str, Any] = Field(
        ...,
        alias='nativeUnit',
        description='Determinate quantity used in the original measurement.',
        title='nativeUnit',
    )
