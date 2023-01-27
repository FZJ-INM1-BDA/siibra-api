import siibra
import pytest
from api.serialization.util import instance_to_model
from api.serialization.util.siibra import Space, spaces
from api.models.core.space import CommonCoordinateSpaceModel

all_spaces = [s for s in spaces]

@pytest.mark.parametrize("space", all_spaces)
def test_space(space: Space):
    model = instance_to_model(space)
    assert isinstance(model, CommonCoordinateSpaceModel)
    model.dict()

