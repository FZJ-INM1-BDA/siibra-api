# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/core/v4/research/subjectGroupState.schema.json

from typing import Any, List, Optional, Union

from pydantic import Field
from new_api.v3.models.openminds.base import SiibraBaseModel


class AgeItem(SiibraBaseModel):
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


class AgeItem1(SiibraBaseModel):
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


class WeightItem(SiibraBaseModel):
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


class WeightItem1(SiibraBaseModel):
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


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    additional_remarks: Optional[str] = Field(
        None,
        alias='additionalRemarks',
        description='Mention of what deserves additional attention or notice.',
        title='additionalRemarks',
    )
    age: Optional[
        Union[
            'AgeItem',
            'AgeItem1',
        ]
    ] = Field(None, alias='age')
    age_category: List[Any] = Field(
        ...,
        alias='ageCategory',
        description='Distinct life cycle class that is defined by a similar age or age range (developmental stage) within a group of individual beings.',
        min_items=1,
        title='ageCategory',
    )
    attribute: Optional[List[Any]] = Field(
        None,
        alias='attribute',
        min_items=1,
        title='attribute',
    )
    handedness: Optional[List[Any]] = Field(
        None,
        alias='handedness',
        description='Degree to which an organism prefers one hand or foot over the other hand or foot during the performance of a task.',
        min_items=1,
        title='handedness',
    )
    lookup_label: Optional[str] = Field(
        None,
        alias='lookupLabel',
        title='lookupLabel',
    )
    pathology: Optional[List[Any]] = Field(
        None,
        alias='pathology',
        description='Structural and functional deviation from the normal that constitutes a disease or characterizes a particular disease.',
        min_items=1,
        title='pathology',
    )
    weight: Optional[
        Union[
            'WeightItem',
            'WeightItem1',
        ]
    ] = Field(None, alias='weight')
