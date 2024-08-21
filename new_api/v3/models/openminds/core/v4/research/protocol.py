# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/core/v4/research/protocol.schema.json

from typing import Any, List, Optional

from pydantic import Field
from new_api.v3.models.openminds.base import SiibraBaseModel


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    description: str = Field(
        ...,
        alias='description',
        description='Longer statement or account giving the characteristics of someone or something.',
        title='description',
    )
    name: str = Field(
        ...,
        alias='name',
        description='Word or phrase that constitutes the distinctive designation of a being or thing.',
        title='name',
    )
    stimulation: Optional[List[Any]] = Field(
        None,
        alias='stimulation',
        min_items=1,
        title='stimulation',
    )
    technique: List[Any] = Field(
        ...,
        alias='technique',
        description='Method of accomplishing a desired aim.',
        min_items=1,
        title='technique',
    )
