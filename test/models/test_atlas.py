import siibra
import pytest
from app.models import instance_to_model

all_atlases = [s for s in siibra.REGISTRY[siibra.Atlas]]

@pytest.mark.parametrize("atlas", all_atlases)
def test_atlas(atlas: siibra.Atlas):
    model = instance_to_model(atlas)
    model.dict()



