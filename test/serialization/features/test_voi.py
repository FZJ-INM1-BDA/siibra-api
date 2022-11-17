from siibra import REGISTRY
from siibra.features.voi import VolumeOfInterest
import pytest
from app.serialization.util import instance_to_model
from models.features.voi import VOIDataModel

all_vois = [v for v in REGISTRY[VolumeOfInterest]]
@pytest.mark.parametrize('voi', all_vois)
def test_voi(voi: VolumeOfInterest):
    model = instance_to_model(voi)
    assert isinstance(model, VOIDataModel)
    model = instance_to_model(voi, detail=True)
    model.dict()
