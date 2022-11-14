# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/computation/v1/dataAnalysis.schema.json

from typing import Any, Dict, List, Optional, Union

from pydantic import Field
from app.models.openminds.base import SiibraBaseModel


class ResourceUsageItem(SiibraBaseModel):
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


class ResourceUsageItem1(SiibraBaseModel):
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
    environment: Dict[str, Any] = Field(
        ..., alias='environment', title='environment'
    )
    input: Optional[Dict[str, Any]] = Field(
        None,
        alias='input',
        description='Something or someone that is put into or participates in a process or machine.',
        title='input',
    )
    launch_configuration: Dict[str, Any] = Field(
        ...,
        alias='launchConfiguration',
        title='launchConfiguration',
    )
    output: Optional[Dict[str, Any]] = Field(
        None,
        alias='output',
        description='Something or someone that comes out of, is delivered or produced by a process or machine.',
        title='output',
    )
    resource_usage: Optional[
        Union[
            'ResourceUsageItem',
            'ResourceUsageItem1',
        ]
    ] = Field(None, alias='resourceUsage')
    started_by: Optional[Dict[str, Any]] = Field(
        None, alias='startedBy', title='startedBy'
    )
    status: Optional[Dict[str, Any]] = Field(
        None, alias='status', title='status'
    )
    tags: Optional[List[str]] = Field(
        None,
        alias='tags',
        min_items=1,
        title='tags',
        unique_items=True,
    )
    was_informed_by: Optional[
        Dict[str, Any]
    ] = Field(
        None,
        alias='wasInformedBy',
        title='wasInformedBy',
    )
