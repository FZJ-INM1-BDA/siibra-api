import siibra
import pytest
from api.serialization.util import instance_to_model
from api.models.core.parcellation import SiibraParcellationModel
from api.serialization.util.siibra import parcellations, Parcellation

all_parcellations = [p for p in parcellations]

@pytest.mark.parametrize("parc", all_parcellations)
def test_parcellations(parc: Parcellation):
    model = instance_to_model(parc)
    assert isinstance(model, SiibraParcellationModel)
    model.dict()
