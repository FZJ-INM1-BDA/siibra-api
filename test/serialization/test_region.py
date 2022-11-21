import siibra
import pytest
from app.serialization.util import instance_to_model
from models.core.region import ParcellationEntityVersionModel

all_parcellations = [p for p in siibra.REGISTRY[siibra.Parcellation]]

@pytest.mark.parametrize("parc", all_parcellations)
def test_regions(parc: siibra.Parcellation):
    for r in parc.regiontree:
        model = instance_to_model(r)
        assert isinstance(model, ParcellationEntityVersionModel)
        model.dict()

