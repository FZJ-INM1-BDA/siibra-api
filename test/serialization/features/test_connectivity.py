import pytest
from api.serialization.util import instance_to_model
from api.models.features._basetypes.regional_connectivity import SiibraRegionalConnectivityModel
from api.serialization.util.siibra import RegionalConnectivity, StreamlineLengths, StreamlineCounts, FunctionalConnectivity

streamline_counts = [f for f in StreamlineCounts.get_instances()]
streamline_lengths = [f for f in StreamlineLengths.get_instances()]
functional_conn = [f for f in FunctionalConnectivity.get_instances()]

all_connectivity = [
    *streamline_counts,
    *streamline_lengths,
    *functional_conn,
]

@pytest.mark.parametrize('conn', all_connectivity)
def test_conn(conn: RegionalConnectivity):
    model = instance_to_model(conn)
    assert isinstance(model, SiibraRegionalConnectivityModel)
    model.dict()

# first_two = [
#     *streamline_counts[:2],
#     *streamline_lengths[:2],
#     *functional_conn[:2],
# ]

# @pytest.mark.parametrize('conn', first_two)
# def test_conn_detail(conn: RegionalConnectivity):
#     model = instance_to_model(conn, detail=True)
#     assert isinstance(model, ConnectivityMatrixDataModel)
#     assert model.matrix
#     assert model.matrix.content
    