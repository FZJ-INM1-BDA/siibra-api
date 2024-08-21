# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/SANDS/v3/atlas/atlasAnnotation.schema.json

from typing import Any, Dict, List, Optional

from pydantic import Field, constr
from new_api.v3.models.openminds.base import SiibraBaseModel


class Coordinates(SiibraBaseModel):
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


class BestViewPoint(SiibraBaseModel):
    coordinate_space: Any = Field(
        ...,
        alias='coordinateSpace',
        description='Two or three dimensional geometric setting.',
        title='coordinateSpace',
    )
    coordinates: 'Coordinates' = Field(
        ..., description='Structured information on a quantitative value.'
    )


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    best_view_point: Optional[
        'BestViewPoint'
    ] = Field(
        None,
        alias='bestViewPoint',
        description='Structured information on a coordinate point.',
    )
    criteria: Optional[Dict[str, Any]] = Field(
        None,
        alias='criteria',
        description='Aspects or standards on which a judgement or decision is based.',
        title='criteria',
    )
    criteria_quality_type: Dict[str, Any] = Field(
        ...,
        alias='criteriaQualityType',
        description='Distinct class that defines how the judgement or decision was made for a particular criteria.',
        title='criteriaQualityType',
    )
    display_color: Optional[
        constr(regex=r'^#[0-9A-Fa-f]{6}$')
    ] = Field(
        None,
        alias='displayColor',
        description='Preferred coloring.',
        title='displayColor',
    )
    inspired_by: Optional[List[Any]] = Field(
        None,
        alias='inspiredBy',
        description='Reference to an inspiring element.',
        min_items=1,
        title='inspiredBy',
    )
    internal_identifier: str = Field(
        ...,
        alias='internalIdentifier',
        description='Term or code that identifies someone or something within a particular product.',
        title='internalIdentifier',
    )
    laterality: Optional[List[Any]] = Field(
        None,
        alias='laterality',
        description='Differentiation between a pair of lateral homologous parts of the body.',
        max_items=2,
        min_items=1,
        title='laterality',
    )
    visualized_in: Optional[Dict[str, Any]] = Field(
        None,
        alias='visualizedIn',
        description='Reference to an image in which something is visible.',
        title='visualizedIn',
    )
