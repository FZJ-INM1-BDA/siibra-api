# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/SANDS/v3/atlas/parcellationEntityVersion.schema.json

from typing import Any, List, Optional, Union

from pydantic import Field, constr
from api.models.openminds.base import SiibraBaseModel


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
    coordinates: List['Coordinates'] = Field(
        ..., description='Structured information on a quantitative value.'
    )


class HasAnnotation(SiibraBaseModel):
    best_view_point: Optional['BestViewPoint'] = Field(
        None,
        alias='bestViewPoint',
        description='Structured information on a coordinate point.',
    )
    criteria: Optional[Any] = Field(
        None,
        description='Aspects or standards on which a judgement or decision is based.',
        title='criteria',
    )
    criteria_quality_type: Any = Field(
        ...,
        alias='criteriaQualityType',
        description='Distinct class that defines how the judgement or decision was made for a particular criteria.',
        title='criteriaQualityType',
    )
    display_color: Optional[constr(regex=r'^#[0-9A-Fa-f]{6}$')] = Field(
        None,
        alias='displayColor',
        description='Preferred coloring.',
        title='displayColor',
    )
    inspired_by: Optional[List] = Field(
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
    laterality: Optional[List] = Field(
        None,
        description='Differentiation between a pair of lateral homologous parts of the body.',
        max_items=2,
        min_items=1,
        title='laterality',
    )
    visualized_in: Optional[Any] = Field(
        None,
        alias='visualizedIn',
        description='Reference to an image in which something is visible.',
        title='visualizedIn',
    )


class RelationAssessmentItem(SiibraBaseModel):
    criteria: Optional[Any] = Field(
        None,
        description='Aspects or standards on which a judgement or decision is based.',
        title='criteria',
    )
    in_relation_to: Any = Field(
        ...,
        alias='inRelationTo',
        description='Reference to a related element.',
        title='inRelationTo',
    )
    qualitative_overlap: Any = Field(
        ...,
        alias='qualitativeOverlap',
        description='Semantic characterization of how much two things occupy the same space.',
        title='qualitativeOverlap',
    )


class QuantitativeOverlapItem(SiibraBaseModel):
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


class QuantitativeOverlapItem1(SiibraBaseModel):
    max_value: float = Field(
        ...,
        alias='maxValue',
        description='Greatest quantity attained or allowed.',
        title='maxValue',
    )
    max_value_unit: Optional[Any] = Field(
        None, alias='maxValueUnit', title='maxValueUnit'
    )
    min_value: float = Field(
        ...,
        alias='minValue',
        description='Smallest quantity attained or allowed.',
        title='minValue',
    )
    min_value_unit: Optional[Any] = Field(
        None, alias='minValueUnit', title='minValueUnit'
    )


class RelationAssessmentItem1(SiibraBaseModel):
    criteria: Optional[Any] = Field(
        None,
        description='Aspects or standards on which a judgement or decision is based.',
        title='criteria',
    )
    in_relation_to: Any = Field(
        ...,
        alias='inRelationTo',
        description='Reference to a related element.',
        title='inRelationTo',
    )
    quantitative_overlap: Union[
        'QuantitativeOverlapItem', 'QuantitativeOverlapItem1'
    ] = Field(..., alias='quantitativeOverlap')


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    has_annotation: Optional[
        'HasAnnotation'
    ] = Field(None, alias='hasAnnotation')
    has_parent: Optional[List[Any]] = Field(
        None,
        alias='hasParent',
        description='Reference to a parent object or legal person.',
        min_items=1,
        title='hasParent',
    )
    lookup_label: Optional[str] = Field(
        None,
        alias='lookupLabel',
        title='lookupLabel',
    )
    name: Optional[str] = Field(
        None,
        alias='name',
        description='Word or phrase that constitutes the distinctive designation of a being or thing.',
        title='name',
    )
    ontology_identifier: Optional[List[str]] = Field(
        None,
        alias='ontologyIdentifier',
        description='Term or code used to identify something or someone registered within a particular ontology.',
        min_items=1,
        title='ontologyIdentifier',
    )
    relation_assessment: Optional[
        Union[
            'RelationAssessmentItem',
            'RelationAssessmentItem1',
        ]
    ] = Field(None, alias='relationAssessment')
    version_identifier: str = Field(
        ...,
        alias='versionIdentifier',
        description='Term or code used to identify the version of something.',
        title='versionIdentifier',
    )
    version_innovation: Optional[str] = Field(
        None,
        alias='versionInnovation',
        description='Documentation on what changed in comparison to a previously published form of something.',
        title='versionInnovation',
    )
