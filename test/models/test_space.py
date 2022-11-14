import siibra
import pytest
from app.models import instance_to_model

all_spaces = [s for s in siibra.REGISTRY[siibra.Space]]

@pytest.mark.parametrize("space", all_spaces)
def test_space(space: siibra.Space):
    model = instance_to_model(space)
    model.dict()



