import siibra
import pytest
from api.serialization.util import instance_to_model
from api.models.core.region import ParcellationEntityVersionModel

all_parcellations = [p for p in siibra.Parcellation.registry()]

@pytest.mark.parametrize("parc", all_parcellations)
def test_regions(parc: siibra.Parcellation):
    for r in parc:
        model = instance_to_model(r)
        assert isinstance(model, ParcellationEntityVersionModel)
        model.dict()

