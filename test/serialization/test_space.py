import siibra
import pytest
from api.serialization.util import instance_to_model
from api.models.core.space import commonCoordinateSpace

all_spaces = [s for s in siibra.Space.registry()]

@pytest.mark.parametrize("space", all_spaces)
def test_space(space: siibra.Space):
    model = instance_to_model(space)
    assert isinstance(model, commonCoordinateSpace.Model)
    model.dict()



