import siibra
import pytest
from api.serialization.util import instance_to_model
from api.models.core.parcellation import SiibraParcellationModel

all_parcellations = [p for p in siibra.Parcellation.registry()]

@pytest.mark.parametrize("parc", all_parcellations)
def test_parcellations(parc: siibra.Parcellation):
    model = instance_to_model(parc)
    assert isinstance(model, SiibraParcellationModel)
    model.dict()
