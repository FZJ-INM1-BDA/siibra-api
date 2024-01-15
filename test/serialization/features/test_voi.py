import pytest
from api.serialization.util import instance_to_model
from api.serialization.util.siibra import Feature, Image
from api.models.features._basetypes.volume_of_interest import (
    SiibraVoiModel
)

features = [feat 
            for Cls in Feature._SUBCLASSES[Image]
            for feat in Cls._get_instances()]

def test_len():
    assert len(features) > 0

@pytest.mark.parametrize('voi', features)
def test_voi(voi: Image):
    assert isinstance(voi, Image)

    model = instance_to_model(voi)
    assert isinstance(model, SiibraVoiModel)
    model = instance_to_model(voi, detail=True)
    model.dict()
