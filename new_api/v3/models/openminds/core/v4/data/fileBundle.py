# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/core/v4/data/fileBundle.schema.json

from typing import Any, Dict, List, Optional

from pydantic import Field
from new_api.v3.models.openminds.base import SiibraBaseModel


class Hash(SiibraBaseModel):
    algorithm: str = Field(
        ...,
        description='Procedure for solving a mathematical problem in a finite number of steps. Can involve repetition of an operation.',
        title='algorithm',
    )
    digest: str = Field(
        ...,
        description='Summation or condensation of a body of information.',
        title='digest',
    )


class StorageSize(SiibraBaseModel):
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
    content_description: Optional[str] = Field(
        None,
        alias='contentDescription',
        title='contentDescription',
    )
    descended_from: Optional[Dict[str, Any]] = Field(
        None,
        alias='descendedFrom',
        title='descendedFrom',
    )
    format: Optional[Dict[str, Any]] = Field(
        None,
        alias='format',
        description='Method of digitally organizing and structuring data or information.',
        title='format',
    )
    grouping_type: Optional[Dict[str, Any]] = Field(
        None,
        alias='groupingType',
        title='groupingType',
    )
    hash: Optional[
        'Hash'
    ] = Field(
        None,
        alias='hash',
        description='Structured information on a hash.',
    )
    is_part_of: Dict[str, Any] = Field(
        ...,
        alias='isPartOf',
        description='Reference to the ensemble of multiple things or beings.',
        title='isPartOf',
    )
    name: str = Field(
        ...,
        alias='name',
        description='Word or phrase that constitutes the distinctive designation of a being or thing.',
        title='name',
    )
    storage_size: Optional[
        'StorageSize'
    ] = Field(
        None,
        alias='storageSize',
        description='Structured information on a quantitative value.',
    )
