# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/HumanBrainProject/openMINDS/3fa86f956b407b2debf47c2e1b6314e37579c707/v3/SANDS/v3/miscellaneous/qualitativeRelationAssessment.schema.json

from typing import Any, Dict, Optional

from pydantic import Field
from new_api.v3.models.openminds.base import SiibraBaseModel


class Model(SiibraBaseModel):
    id: str = Field(..., alias='@id', description='Metadata node identifier.')
    type: str = Field(..., alias='@type')
    criteria: Optional[Dict[str, Any]] = Field(
        None,
        alias='criteria',
        description='Aspects or standards on which a judgement or decision is based.',
        title='criteria',
    )
    in_relation_to: Dict[str, Any] = Field(
        ...,
        alias='inRelationTo',
        description='Reference to a related element.',
        title='inRelationTo',
    )
    qualitative_overlap: Dict[str, Any] = Field(
        ...,
        alias='qualitativeOverlap',
        description='Semantic characterization of how much two things occupy the same space.',
        title='qualitativeOverlap',
    )
