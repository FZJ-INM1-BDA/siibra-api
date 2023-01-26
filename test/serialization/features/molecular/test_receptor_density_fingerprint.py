from api.serialization.util.siibra import (
    ReceptorDensityFingerprint,
)
from api.models.features.molecular.receptor_density_fingerprint import (
    SiibraReceptorDensityFp
)
import pytest
from api.serialization.util import (
    instance_to_model
)

receptor_fp_feats = ReceptorDensityFingerprint.get_instances()

def test_length():
    assert len(receptor_fp_feats) > 0

@pytest.mark.parametrize('feat', receptor_fp_feats)
def test_fp_feats(feat: ReceptorDensityFingerprint):
    assert isinstance(feat, ReceptorDensityFingerprint)
    model = instance_to_model(feat)
    assert isinstance(model, SiibraReceptorDensityFp)
