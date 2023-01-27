# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/core/v4/research/subject.schema.json

from typing import Any, Dict, List, Optional

from pydantic import Field
from api.models.openminds.base import SiibraBaseModel


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    biological_sex: Optional[Dict[str, Any]] = Field(
        None,
        alias='biologicalSex',
        description='Differentiation of individuals of most species (animals and plants) based on the type of gametes they produce.',
        title='biologicalSex',
    )
    internal_identifier: Optional[str] = Field(
        None,
        alias='internalIdentifier',
        description='Term or code that identifies someone or something within a particular product.',
        title='internalIdentifier',
    )
    is_part_of: Optional[List[Any]] = Field(
        None,
        alias='isPartOf',
        description='Reference to the ensemble of multiple things or beings.',
        min_items=1,
        title='isPartOf',
    )
    lookup_label: Optional[str] = Field(
        None,
        alias='lookupLabel',
        title='lookupLabel',
    )
    species: Dict[str, Any] = Field(
        ...,
        alias='species',
        description='Category of biological classification comprising related organisms or populations potentially capable of interbreeding, and being designated by a binomial that consists of the name of a genus followed by a Latin or latinized uncapitalized noun or adjective.',
        title='species',
    )
    studied_state: List[Any] = Field(
        ...,
        alias='studiedState',
        description='Reference to a point in time at which something or someone was studied in a particular mode or condition.',
        min_items=1,
        title='studiedState',
    )
