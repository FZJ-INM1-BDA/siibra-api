from api.serialization.util.siibra import (
    AnatomicalAnchor,
    AnatomicalAssignment,
    Region,
)
from api.models.features.anchor import (
    SiibraAnchorModel,
    SiibraRegionAssignmentQual,
    SiibraAnatomicalAssignmentModel,
)
from api.serialization.util import (
    serialize,
    instance_to_model
)

@serialize(AnatomicalAssignment)
def assignment_to_model(asgmt: AnatomicalAssignment, detail: bool=False, **kwargs) -> SiibraAnatomicalAssignmentModel:
    """Serialize AnatommicalAssignment instance

    Args:
        asgmt: siibra AnatomicalAssignment instance
        detail: detail flag.
    
    Returns:
        SiibraAnatomicalAssignmentModel

    """
    return SiibraAnatomicalAssignmentModel(
        query_structure=instance_to_model(asgmt.query_structure, detail=detail, **kwargs),
        assigned_structure=instance_to_model(asgmt.assigned_structure, detail=detail, **kwargs),
        qualification=asgmt.qualification.name,
        explanation=asgmt.explanation,
    )

@serialize(AnatomicalAnchor)
def anchor_to_model(anchor: AnatomicalAnchor, detail=False, **kwargs):
    return SiibraAnchorModel(
        location=instance_to_model(anchor.location, detail=detail, **kwargs),
        regions=[SiibraRegionAssignmentQual(
            region=instance_to_model(region, use_class=Region, min_flag=True, **kwargs),
            qualification=qualification.name
        ) for region, qualification in anchor.regions.items()],
        last_match_description=anchor.last_match_description or "",
        last_match_result=instance_to_model(anchor.last_match_result or [], detail=detail, **kwargs)
    )
