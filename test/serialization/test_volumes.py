import siibra
import pytest
from app.serialization.util import instance_to_model
from models.volumes.volume import VolumeModel
from siibra.volumes.volume import VolumeSrc

some_volumes = [
    *[v
    for p in siibra.REGISTRY[siibra.Parcellation]
    for v in p.volumes],
    *[v
    for s in siibra.REGISTRY[siibra.Space]
    for v in s.volumes]
]

@pytest.mark.parametrize('volume', some_volumes)
def test_volumes(volume: VolumeSrc):
    model = instance_to_model(volume)
    assert isinstance(model, VolumeModel)
    model.dict()
