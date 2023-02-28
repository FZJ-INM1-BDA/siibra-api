import pytest
from api.serialization.util import instance_to_model
from api.models.features._basetypes.regional_connectivity import SiibraRegionalConnectivityModel
from api.serialization.util.siibra import RegionalConnectivity, StreamlineLengths, StreamlineCounts, FunctionalConnectivity, parcellations
import os

jba29 = parcellations['2.9']

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


if not os.getenv("FAST_RUN"):
    @pytest.mark.parametrize("conn,subject",
                            [(f, s)
                                for f in all_connectivity
                                if jba29 in f.anchor.parcellations
                                for s in f.subjects],
                            ids=lambda arg: f"name: {arg.name!r} paradigm: {arg.paradigm if hasattr(arg, 'paradigmn') else ''}"
                                if isinstance(arg, RegionalConnectivity)
                                else f"subject: {arg!r}")
    def test_conn_subject(conn: RegionalConnectivity, subject: str):
        model = instance_to_model(conn, subject=subject, detail=True)
        assert isinstance(model, SiibraRegionalConnectivityModel)
        assert model.matrices is not None
        model.dict()
