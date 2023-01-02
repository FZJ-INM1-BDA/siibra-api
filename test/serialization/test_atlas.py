import siibra
import pytest
from api.serialization.util import instance_to_model
from api.models.core.atlas import SiibraAtlasModel

all_atlases = [s for s in siibra.Atlas.registry()]

@pytest.mark.parametrize("atlas", all_atlases)
def test_atlas(atlas: siibra.Atlas):
    model = instance_to_model(atlas)
    assert isinstance(model, SiibraAtlasModel)
    model.dict()



