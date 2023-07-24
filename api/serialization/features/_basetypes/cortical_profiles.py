from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import CorticalProfile
from api.models.features._basetypes.cortical_profiles import SiibraCorticalProfileModel

@serialize(CorticalProfile, pass_super_model=True)
def cortical_profile_to_model(pr: CorticalProfile, detail=False, super_model_dict={}, **kwargs) -> SiibraCorticalProfileModel:
    """Serialize cortical profile into SiibraCorticalProfileModel.

    As serialize.pass_super_model is set to true, the instance will first be serialized according to its superclass of CorticalProfile (Tabular),
    and passed to this function as super_model_dict. User **should** not supply their own `super_model_dict` kwarg, as it will be ignored.
    
    Args:
        pr: instance of CorticalProfile to be serialized

    Returns:
        SiibraCorticalProfileModel
    """

    return SiibraCorticalProfileModel(
        **super_model_dict,
        unit=pr.unit,
        boundary_positions={
            "-".join([str(bound) for bound in boundary]): val
            for boundary, val in pr.boundary_positions.items()
        },
        boundaries_mapped=pr.boundaries_mapped,
    )
