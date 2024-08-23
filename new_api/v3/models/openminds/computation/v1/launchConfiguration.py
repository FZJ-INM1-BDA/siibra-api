# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/computation/v1/launchConfiguration.schema.json

from typing import Any, Dict, List, Optional

from pydantic import Field
from new_api.v3.models.openminds.base import SiibraBaseModel


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    arguments: Optional[List[str]] = Field(
        None,
        alias='arguments',
        min_items=1,
        title='arguments',
    )
    description: Optional[str] = Field(
        None,
        alias='description',
        description='Longer statement or account giving the characteristics of someone or something.',
        title='description',
    )
    environment_variables: Optional[
        Dict[str, Any]
    ] = Field(
        None,
        alias='environmentVariables',
        title='environmentVariables',
    )
    executable: str = Field(
        ..., alias='executable', title='executable'
    )
    name: Optional[str] = Field(
        None,
        alias='name',
        description='Word or phrase that constitutes the distinctive designation of a being or thing.',
        title='name',
    )