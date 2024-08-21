# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/core/v4/products/dataset.schema.json

from typing import Any, Dict, List, Optional

from pydantic import Field, constr
from new_api.v3.models.openminds.base import SiibraBaseModel


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    author: List[Any] = Field(
        ...,
        alias='author',
        description='Creator of a literary or creative work, as well as a dataset publication.',
        min_items=1,
        title='author',
    )
    custodian: Optional[List[Any]] = Field(
        None,
        alias='custodian',
        description="The 'custodian' is a legal person who is responsible for the content and quality of the data, metadata, and/or code of a research product.",
        min_items=1,
        title='custodian',
    )
    description: constr(max_length=2000) = Field(
        ...,
        alias='description',
        description='Longer statement or account giving the characteristics of someone or something.',
        title='description',
    )
    digital_identifier: Optional[
        Dict[str, Any]
    ] = Field(
        None,
        alias='digitalIdentifier',
        description='Digital handle to identify objects or legal persons.',
        title='digitalIdentifier',
    )
    full_name: str = Field(
        ...,
        alias='fullName',
        description='Whole, non-abbreviated name of something or somebody.',
        title='fullName',
    )
    has_version: List[Any] = Field(
        ...,
        alias='hasVersion',
        description='Reference to variants of an original.',
        min_items=1,
        title='hasVersion',
    )
    homepage: Optional[Dict[str, Any]] = Field(
        None,
        alias='homepage',
        description='Main website of something or someone.',
        title='homepage',
    )
    how_to_cite: Optional[str] = Field(
        None,
        alias='howToCite',
        description='Preferred format for citing a particular object or legal person.',
        title='howToCite',
    )
    short_name: constr(max_length=30) = Field(
        ...,
        alias='shortName',
        description='Shortened or fully abbreviated name of something or somebody.',
        title='shortName',
    )
