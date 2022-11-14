from app.models import instance_to_model
import siibra
import pytest
from siibra.core.datasets import Dataset

query = siibra.features.EbrainsRegionalFeatureQuery()

all_features = [f for f in query.features]

@pytest.mark.parametrize("ds", all_features)
def test_dataset(ds: Dataset):
    model = instance_to_model(ds)
    model.dict()
