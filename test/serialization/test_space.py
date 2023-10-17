import siibra
import pytest
from api.serialization.util import instance_to_model
from api.serialization.util.siibra import Space, spaces
from api.models.core.space import CommonCoordinateSpaceModel

all_spaces = [s for s in spaces]
spaces_without_ds = ("ICBM 2009c nonl asym", "Allen Mouse CCF v3", "hcp32k")

@pytest.mark.parametrize("space", all_spaces)
def test_space(space: Space):
    model = instance_to_model(space)
    assert isinstance(model, CommonCoordinateSpaceModel)
    model.dict()
    if model.short_name not in spaces_without_ds:
        assert len(model.datasets) > 0
