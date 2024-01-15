import pytest
from api.serialization.util import instance_to_model
from api.models.features._basetypes.regional_connectivity import SiibraRegionalConnectivityModel
from api.serialization.util.siibra import RegionalConnectivity, StreamlineLengths, StreamlineCounts, FunctionalConnectivity, parcellations
import os

jba29 = parcellations['2.9']

streamline_counts = [f for f in StreamlineCounts._get_instances()]
streamline_lengths = [f for f in StreamlineLengths._get_instances()]
functional_conn = [f for f in FunctionalConnectivity._get_instances()]

all_connectivity: list[RegionalConnectivity] = [
    *streamline_counts,
    *streamline_lengths,
    *functional_conn,
]

@pytest.mark.parametrize('conn', all_connectivity)
def test_conn(conn: RegionalConnectivity):
    model = instance_to_model(conn)
    assert isinstance(model, SiibraRegionalConnectivityModel)
    model.dict()


if not os.getenv("FAST_RUN"):
    @pytest.mark.parametrize("conn,subject",
                            [(f, f.subject)
                                for f in all_connectivity
                                if jba29 in f.anchor.parcellations],
                            ids=lambda arg: f"name: {arg.name!r} paradigm: {arg.paradigm if hasattr(arg, 'paradigmn') else ''}"
                                if isinstance(arg, RegionalConnectivity)
                                else f"subject: {arg!r}")
    def test_conn_subject(conn: RegionalConnectivity, subject: str):
        model = instance_to_model(conn, subject=subject, detail=True)
        assert isinstance(model, SiibraRegionalConnectivityModel)
        assert model.matrix is not None
        model.dict()
