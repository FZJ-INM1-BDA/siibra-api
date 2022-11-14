# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/core/v4/data/contentTypePattern.schema.json

from typing import Any, Dict, Optional

from pydantic import Field
from app.models.openminds.base import SiibraBaseModel


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    content_type: Dict[str, Any] = Field(
        ..., alias='contentType', title='contentType'
    )
    lookup_label: Optional[str] = Field(
        None,
        alias='lookupLabel',
        title='lookupLabel',
    )
    regex: str = Field(
        ..., alias='regex', title='regex'
    )
