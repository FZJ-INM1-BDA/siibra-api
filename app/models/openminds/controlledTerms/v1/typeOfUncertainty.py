# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/controlledTerms/v1/typeOfUncertainty.schema.json

from typing import List, Optional

from pydantic import Field
from app.models.openminds.base import SiibraBaseModel


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    definition: Optional[str] = Field(
        None,
        alias='definition',
        description='Short, but precise statement of the meaning of a word, word group, sign or a symbol.',
        title='definition',
    )
    description: Optional[str] = Field(
        None,
        alias='description',
        description='Longer statement or account giving the characteristics of someone or something.',
        title='description',
    )
    interlex_identifier: Optional[str] = Field(
        None,
        alias='interlexIdentifier',
        description='Persistent identifier for a term registered in the InterLex project.',
        title='interlexIdentifier',
    )
    knowledge_space_link: Optional[str] = Field(
        None,
        alias='knowledgeSpaceLink',
        description='Persistent link to an encyclopedia entry in the Knowledge Space project.',
        title='knowledgeSpaceLink',
    )
    name: str = Field(
        ...,
        alias='name',
        description='Word or phrase that constitutes the distinctive designation of a being or thing.',
        title='name',
    )
    preferred_ontology_identifier: Optional[
        str
    ] = Field(
        None,
        alias='preferredOntologyIdentifier',
        description='Persistent identifier of a preferred ontological term.',
        title='preferredOntologyIdentifier',
    )
    synonym: Optional[List[str]] = Field(
        None,
        alias='synonym',
        description='Words or expressions used in the same language that have the same or nearly the same meaning in some or all senses.',
        min_items=1,
        title='synonym',
        unique_items=True,
    )
