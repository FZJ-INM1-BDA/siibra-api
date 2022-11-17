import siibra
import pytest
from app.serialization.util import instance_to_model
from models.core.atlas import SiibraAtlasModel

all_atlases = [s for s in siibra.REGISTRY[siibra.Atlas]]

@pytest.mark.parametrize("atlas", all_atlases)
def test_atlas(atlas: siibra.Atlas):
    model = instance_to_model(atlas)
    assert isinstance(model, SiibraAtlasModel)
    model.dict()



