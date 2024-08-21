# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/core/v4/actors/contactInformation.schema.json

from pydantic import EmailStr, Field
from new_api.v3.models.openminds.base import SiibraBaseModel


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    email: EmailStr = Field(
        ...,
        alias='email',
        description='Address to which or from which an electronic mail can be sent.',
        title='email',
    )
