from api.serialization.util.siibra import (
    AnatomicalAnchor
)
from api.models.features.anchor import (
    SiibraAnchorModel,
    SiibraRegionAssignmentQual,
)
from api.serialization.util import (
    serialize,
    instance_to_model
)

@serialize(AnatomicalAnchor)
def anchor_to_model(anchor: AnatomicalAnchor, detail=False, **kwargs):
    return SiibraAnchorModel(
        location=instance_to_model(anchor.location, detail=detail, **kwargs),
        regions=[SiibraRegionAssignmentQual(
            region=instance_to_model(region, **kwargs),
            qualification=qualification.name
        ) for region, qualification in anchor.regions.items()]
    )
