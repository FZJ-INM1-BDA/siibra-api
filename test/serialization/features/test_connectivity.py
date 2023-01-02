from siibra.features.connectivity import (
    StreamlineCounts,
    StreamlineLengths,
    FunctionalConnectivity,
    ConnectivityMatrix,
)
from siibra import REGISTRY
import pytest
from api.serialization.util import instance_to_model
from api.models.features.connectivity import ConnectivityMatrixDataModel

streamline_counts = [f for f in REGISTRY[StreamlineCounts]]
streamline_lengths = [f for f in REGISTRY[StreamlineLengths]]
functional_conn = [f for f in REGISTRY[FunctionalConnectivity]]

all_connectivity = [
    *streamline_counts,
    *streamline_lengths,
    *functional_conn,
]

@pytest.mark.parametrize('conn', all_connectivity)
def test_conn(conn: ConnectivityMatrix):
    model = instance_to_model(conn)
    assert isinstance(model, ConnectivityMatrixDataModel)
    model.dict()

first_two = [
    *streamline_counts[:2],
    *streamline_lengths[:2],
    *functional_conn[:2],
]

@pytest.mark.parametrize('conn', first_two)
def test_conn_detail(conn: ConnectivityMatrix):
    model = instance_to_model(conn, detail=True)
    assert isinstance(model, ConnectivityMatrixDataModel)
    assert model.matrix
    assert model.matrix.content
    