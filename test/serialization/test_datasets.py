from app.serialization.util import instance_to_model
import siibra
import pytest
from siibra.core.datasets import Dataset
from models.core.datasets import DatasetJsonModel
import os

query = siibra.features.EbrainsRegionalFeatureQuery()

all_features = [f for f in query.features]
all_features = all_features[:10] if 'FAST_RUN' in os.environ else all_features

@pytest.mark.parametrize("ds", all_features)
def test_dataset(ds: Dataset):
    model = instance_to_model(ds)
    assert isinstance(model, DatasetJsonModel)
    model.dict()
