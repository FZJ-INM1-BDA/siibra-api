from api.serialization.util import serialize, instance_to_model
from api.serialization.util.siibra import (
    ReceptorDensityFingerprint
)
from api.models.features.molecular.receptor_density_fingerprint import (
    SiibraReceptorDensityFp
)

@serialize(ReceptorDensityFingerprint, pass_super_model=True)
def receptor_density_to_model(fp: ReceptorDensityFingerprint, detail=False, super_model_dict={}, **kwargs):
    return SiibraReceptorDensityFp(
        **super_model_dict,
        receptors=fp.receptors if detail else None,
        neurotransmitters=fp.neurotransmitters if detail else None,
    )
