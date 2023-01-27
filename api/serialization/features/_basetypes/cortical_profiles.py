from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import CorticalProfile
from api.models.features._basetypes.cortical_profiles import SiibraCorticalProfileModel

@serialize(CorticalProfile, pass_super_model=True)
def cortical_profile_to_model(pr: CorticalProfile, detail=False, super_model_dict={}, **kwargs):
    return SiibraCorticalProfileModel(
        **super_model_dict,
        unit=pr.unit,
        boundary_positions=pr.boundary_positions,
        boundaries_mapped=pr.boundaries_mapped,
        data=instance_to_model(pr.data, detail=detail, **kwargs) if detail else None
    )
