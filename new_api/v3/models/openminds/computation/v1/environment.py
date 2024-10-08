# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/computation/v1/environment.schema.json

from typing import Any, Dict, List, Optional

from pydantic import Field
from new_api.v3.models.openminds.base import SiibraBaseModel


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    configuration: Optional[List[Any]] = Field(
        None,
        alias='configuration',
        min_items=1,
        title='configuration',
    )
    description: Optional[str] = Field(
        None,
        alias='description',
        description='Longer statement or account giving the characteristics of someone or something.',
        title='description',
    )
    hardware: Dict[str, Any] = Field(
        ..., alias='hardware', title='hardware'
    )
    name: str = Field(
        ...,
        alias='name',
        description='Word or phrase that constitutes the distinctive designation of a being or thing.',
        title='name',
    )
    software: Optional[List[Any]] = Field(
        None,
        alias='software',
        min_items=1,
        title='software',
    )
