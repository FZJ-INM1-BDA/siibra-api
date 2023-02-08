import pytest
from api.serialization.util import instance_to_model
from api.models.core.atlas import SiibraAtlasModel
from api.serialization.util.siibra import Atlas, atlases
all_atlases = [s for s in atlases]

@pytest.mark.parametrize("atlas", all_atlases)
def test_atlas(atlas: Atlas):
    model = instance_to_model(atlas)
    assert isinstance(model, SiibraAtlasModel)
    model.dict()
