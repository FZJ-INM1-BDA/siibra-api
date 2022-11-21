import siibra
import pytest
from app.serialization.util import instance_to_model
from models.core.parcellation import SiibraParcellationModel

all_parcellations = [p for p in siibra.REGISTRY[siibra.Parcellation]]

@pytest.mark.parametrize("parc", all_parcellations)
def test_parcellations(parc: siibra.Parcellation):
    model = instance_to_model(parc)
    assert isinstance(model, SiibraParcellationModel)
    model.dict()
