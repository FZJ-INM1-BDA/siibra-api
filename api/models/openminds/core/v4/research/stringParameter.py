# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/core/v4/research/stringParameter.schema.json

from pydantic import Field
from api.models.openminds.base import SiibraBaseModel


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    name: str = Field(
        ...,
        alias='name',
        description='Word or phrase that constitutes the distinctive designation of a being or thing.',
        title='name',
    )
    value: str = Field(
        ...,
        alias='value',
        description='Entry for a property.',
        title='value',
    )
