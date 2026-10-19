"""Tests run against a real siibra 0.4 install.

They need a siibra configuration. Point SIIBRA_USE_CONFIGURATION at a local
clone of siibra-configurations if the default GitLab mirrors are unreachable.
"""
import http.server
import threading

import pytest
import wrapt
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from siibra_otel import SiibraInstrumentor

_exporter = InMemorySpanExporter()
_provider = TracerProvider()
_provider.add_span_processor(SimpleSpanProcessor(_exporter))
trace.set_tracer_provider(_provider)

import siibra  # noqa: E402
from siibra.features.feature import Feature  # noqa: E402


@pytest.fixture
def instrumented():
    inst = SiibraInstrumentor()
    inst.instrument(tracer_provider=_provider)
    _exporter.clear()
    yield inst
    inst.uninstrument()
    _exporter.clear()


@pytest.fixture(scope="module")
def hoc1():
    return siibra.get_region("julich 2.9", "hoc1 left")


def _spans(name):
    return [s for s in _exporter.get_finished_spans() if s.name == name]


def test_feature_get_produces_outer_and_per_type_spans(instrumented, hoc1):
    result = siibra.features.get(hoc1, "receptor")

    matches = _spans("siibra.Feature.match")
    outer = [s for s in matches if "siibra.feature_type.query" in s.attributes]
    per_type = [s for s in matches if "siibra.feature_type" in s.attributes]

    assert len(outer) == 1 and outer[0].parent is None
    assert outer[0].attributes["siibra.result.count"] == len(result)
    assert {s.attributes["siibra.feature_type"] for s in per_type} == {
        "ReceptorDensityFingerprint", "ReceptorDensityProfile"}
    for s in per_type:
        assert s.parent.span_id == outer[0].context.span_id
        assert s.attributes["siibra.match.candidates"] >= s.attributes["siibra.match.preconfigured_hits"]
    # the list-level recursion step does not get its own span
    assert len(matches) == 3


def test_get_instances_and_livequery_are_children(instrumented, hoc1):
    siibra.features.get(hoc1, "receptor fingerprint")
    (match,) = [s for s in _spans("siibra.Feature.match") if "siibra.feature_type" in s.attributes]
    for name in ("siibra.Feature.get_instances", "siibra.Feature.livequery"):
        (s,) = _spans(name)
        assert s.parent.span_id == match.context.span_id


def test_no_per_feature_spans_by_default(instrumented, hoc1):
    siibra.features.get(hoc1, "receptor fingerprint")
    assert _spans("siibra.Feature.matches") == []
    assert _spans("siibra.Parcellation.find_regions") == []


def test_detailed_mode_adds_per_feature_spans(hoc1):
    inst = SiibraInstrumentor()
    inst.instrument(tracer_provider=_provider, detailed=True)
    try:
        _exporter.clear()
        siibra.features.get(hoc1, "receptor fingerprint")
        (match,) = [s for s in _spans("siibra.Feature.match") if "siibra.feature_type" in s.attributes]
        assert len(_spans("siibra.Feature.matches")) == match.attributes["siibra.match.candidates"]
    finally:
        inst.uninstrument()


@pytest.mark.skipif(not __import__("os").environ.get("SIIBRA_OTEL_NETWORK"),
                    reason="resolving spaces downloads from neuroglancer.humanbrainproject.eu")
def test_point_warp_span(instrumented):
    p = siibra.Point((0, 0, 0), space="mni152")
    p.warp("mni152")  # same space: no network, but still traced
    (s,) = _spans("siibra.Location.warp")
    assert s.attributes["siibra.location.type"] == "Point"


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'{"ok": true}'
        self.send_response(200)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def test_http_request_cache_hit_attribute(instrumented):
    from siibra.retrieval.requests import EbrainsRequest, HttpRequest

    server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/data.json?nonce={id(server)}"
    try:
        req = HttpRequest(url, refresh=True)
        assert req.get() == {"ok": True}
        assert HttpRequest(url).get() == {"ok": True}
    finally:
        server.shutdown()

    first, second = _spans("siibra.HttpRequest.get")
    assert first.attributes["siibra.cache_hit"] is False
    assert second.attributes["siibra.cache_hit"] is True
    assert first.attributes["url.full"] == url
    # subclass overrides are patched too, and super() chains collapse to one span
    assert isinstance(vars(EbrainsRequest)["get"], wrapt.FunctionWrapper)


def test_uninstrument_restores_everything(hoc1):
    import siibra.features as features_pkg
    from siibra.features.tabular.receptor_density_fingerprint import ReceptorDensityFingerprint

    original_get = features_pkg.get
    originals = {name: vars(Feature)[name] for name in ("match", "matches", "get_instances", "livequery")}

    inst = SiibraInstrumentor()
    inst.instrument(tracer_provider=_provider)
    assert features_pkg.get is not original_get
    inst.uninstrument()

    assert features_pkg.get is original_get
    for name, desc in originals.items():
        assert vars(Feature)[name] is desc, name
    # classmethods must still bind to the subclass after unwrapping
    assert all(isinstance(f, ReceptorDensityFingerprint) for f in ReceptorDensityFingerprint.get_instances())

    _exporter.clear()
    siibra.features.get(hoc1, "receptor fingerprint")
    assert _exporter.get_finished_spans() == ()
