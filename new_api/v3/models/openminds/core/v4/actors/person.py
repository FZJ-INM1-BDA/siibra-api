# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/core/v4/actors/person.schema.json

from typing import Any, Dict, List, Optional

from pydantic import Field
from new_api.v3.models.openminds.base import SiibraBaseModel


class Affiliation(SiibraBaseModel):
    end_date: Optional[str] = Field(
        None,
        alias='endDate',
        description='Date in the Gregorian calendar at which something terminates in time.',
        title='endDate',
    )
    organization: Any = Field(
        ...,
        description='Legally accountable, administrative and functional structure.',
        title='organization',
    )
    start_date: Optional[str] = Field(
        None,
        alias='startDate',
        description='Date in the Gregorian calendar at which something begins in time',
        title='startDate',
    )


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    affiliation: Optional[
        'Affiliation'
    ] = Field(None, alias='affiliation')
    contact_information: Optional[
        Dict[str, Any]
    ] = Field(
        None,
        alias='contactInformation',
        description='Any available way used to contact a person or business (e.g., address, phone number, email address, etc.).',
        title='contactInformation',
    )
    digital_identifier: Optional[List[Any]] = Field(
        None,
        alias='digitalIdentifier',
        description='Digital handle to identify objects or legal persons.',
        min_items=1,
        title='digitalIdentifier',
    )
    family_name: Optional[str] = Field(
        None,
        alias='familyName',
        description='Name borne in common by members of a family.',
        title='familyName',
    )
    given_name: str = Field(
        ...,
        alias='givenName',
        description='Name given to a person, including all potential middle names, but excluding the family name.',
        title='givenName',
    )
