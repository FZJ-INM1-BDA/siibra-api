import pytest
from api.serialization.util import instance_to_model
from api.models.core.region import ParcellationEntityVersionModel
from api.serialization.util.siibra import parcellations, Parcellation

all_parcellations = [p for p in parcellations]

@pytest.mark.parametrize("parc", all_parcellations)
def test_regions(parc: Parcellation):
    for r in parc:
        if r is parc:
            continue
        model = instance_to_model(r)
        assert isinstance(model, ParcellationEntityVersionModel)
        model.dict()

