import siibra
import pytest
from app.serialization.util import instance_to_model
from models.core.space import commonCoordinateSpace

all_spaces = [s for s in siibra.REGISTRY[siibra.Space]]

@pytest.mark.parametrize("space", all_spaces)
def test_space(space: siibra.Space):
    model = instance_to_model(space)
    assert isinstance(model, commonCoordinateSpace.Model)
    model.dict()



