# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/core/v4/miscellaneous/GRIDID.schema.json

from pydantic import Field, constr
from new_api.v3.models.openminds.base import SiibraBaseModel


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    identifier: constr(
        regex=r'^https://grid.ac/institutes/grid.[0-9]{1,}.([a-f0-9]{1,2})$'
    ) = Field(
        ...,
        alias='identifier',
        description='Term or code used to identify something or someone.',
        title='identifier',
    )
