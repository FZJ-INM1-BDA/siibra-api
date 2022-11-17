from siibra.features import IEEG_SessionQuery
from siibra.features.ieeg import IEEG_Session
import pytest
from app.serialization.util import instance_to_model
from models.features.ieeg import IEEGSessionModel
ieeg_query = IEEG_SessionQuery()

all_ieeg_features = [f for f in ieeg_query.features]

@pytest.mark.parametrize('feature', all_ieeg_features)
def test_ieeg_features(feature: IEEG_Session):
    model = instance_to_model(feature)
    assert isinstance(model, IEEGSessionModel)
    model.dict()
