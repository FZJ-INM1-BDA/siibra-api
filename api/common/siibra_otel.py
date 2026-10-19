"""OpenTelemetry tracing for siibra-python 0.4 (v0.4EOL), without touching siibra.

Requires: opentelemetry-api, opentelemetry-instrumentation, wrapt, siibra>=0.4,<0.5

Usage::

    from siibra_otel import SiibraInstrumentor
    SiibraInstrumentor().instrument()               # coarse spans (default)
    SiibraInstrumentor().instrument(detailed=True)  # + one span per Feature.matches()
                                                    #   and per region-spec decode

For zero-code use with ``opentelemetry-instrument``, register an entry point in
the packaging repo::

    [project.entry-points.opentelemetry_instrumentor]
    siibra = "siibra_otel:SiibraInstrumentor"

Pair it with ``opentelemetry-instrumentation-requests`` to get the raw HTTP
client spans underneath siibra's own download / cache spans.
"""

import contextvars
from contextlib import contextmanager
from typing import Callable, Collection, Dict, List, Optional, Tuple

import wrapt
from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import is_instrumentation_enabled
from opentelemetry.trace import SpanKind

__version__ = "0.1.0"

__all__ = ["SiibraInstrumentor", "__version__"]

_INSTRUMENTS = ("siibra >= 0.4a0, < 0.5",)

# (span name, id(owner)) pairs currently open in this context. Used to collapse
# recursion (match_location_to_region) and subclass -> super() chains
# (EbrainsRequest.get -> HttpRequest.get) into a single span.
_ACTIVE: contextvars.ContextVar = contextvars.ContextVar("siibra_otel_active", default=frozenset())

# Per-feature-type counters filled by the Feature.matches wrapper and read by
# the enclosing Feature.match span.
_MATCH_STATS: contextvars.ContextVar = contextvars.ContextVar("siibra_otel_match_stats", default=None)


def _safe(fn: Callable, *args, default=None):
    try:
        return fn(*args)
    except Exception:  # attribute extraction must never break siibra
        return default


def _arg(args, kwargs, pos: int, name: str, default=None):
    if name in kwargs:
        return kwargs[name]
    return args[pos] if len(args) > pos else default


def _type_name(obj) -> str:
    return obj.__name__ if isinstance(obj, type) else type(obj).__name__


def _concept_attrs(concept) -> Dict[str, str]:
    return {
        "siibra.concept.type": _type_name(concept),
        "siibra.concept.name": str(_safe(lambda: concept.name, default=concept)),
    }


def _space_name(space) -> str:
    if space is None:
        return ""
    return str(_safe(lambda: space.name, default=space))


def _len(result) -> Optional[int]:
    return _safe(len, result)


@contextmanager
def _dedupe(key):
    token = _ACTIVE.set(_ACTIVE.get() | {key})
    try:
        yield
    finally:
        _ACTIVE.reset(token)


class SiibraInstrumentor(BaseInstrumentor):
    """Monkey-patches siibra's expensive entry points with spans."""

    # BaseInstrumentor is a singleton and __init__ runs on every
    # SiibraInstrumentor() call, so state lives on the class, not in __init__.
    _patched: List[Tuple[object, str]] = []
    _features_get_original = None

    def instrumentation_dependencies(self) -> Collection[str]:
        return _INSTRUMENTS

    # ------------------------------------------------------------------ helpers

    def _wrap(self, owner, attr: str, wrapper):
        if attr not in vars(owner):
            return
        if (owner, attr) in self._patched:
            return
        wrapt.wrap_function_wrapper(owner, attr, wrapper)
        self._patched.append((owner, attr))

    def _wrap_hierarchy(self, base: type, attr: str, wrapper):
        """Wrap `attr` on `base` and on every (imported) subclass that overrides it."""
        seen = set()
        stack = [base]
        while stack:
            cls = stack.pop()
            if cls in seen:
                continue
            seen.add(cls)
            self._wrap(cls, attr, wrapper)
            stack.extend(cls.__subclasses__())

    def _span_wrapper(
        self,
        span_name: str,
        attrs: Optional[Callable] = None,
        on_result: Optional[Callable] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        dedupe_on_owner: bool = True,
    ):
        """Build a wrapt wrapper that runs the wrapped call inside a span.

        attrs(instance, args, kwargs) -> dict      evaluated before the call
        on_result(span, result, instance) -> None  evaluated after the call
        """
        tracer = self._tracer

        def wrapper(wrapped, instance, args, kwargs):
            if not is_instrumentation_enabled():
                return wrapped(*args, **kwargs)
            key = (span_name, id(instance)) if dedupe_on_owner else None
            if key is not None and key in _ACTIVE.get():
                return wrapped(*args, **kwargs)
            attributes = _safe(attrs, instance, args, kwargs, default={}) if attrs else {}
            with tracer.start_as_current_span(span_name, kind=kind, attributes=attributes or None) as span:
                if key is None:
                    result = wrapped(*args, **kwargs)
                else:
                    with _dedupe(key):
                        result = wrapped(*args, **kwargs)
                if on_result is not None and span.is_recording():
                    _safe(on_result, span, result, instance)
                return result

        return wrapper

    @staticmethod
    def _set_count(span, result, _instance=None):
        n = _len(result)
        if n is not None:
            span.set_attribute("siibra.result.count", n)

    # -------------------------------------------------------------- instrument

    def _instrument(self, **kwargs):
        self._tracer = trace.get_tracer(
            __name__,
            __version__,
            tracer_provider=kwargs.get("tracer_provider"),
            schema_url="https://opentelemetry.io/schemas/1.26.0",
        )
        detailed = bool(kwargs.get("detailed", False))

        # Import lazily: importing siibra triggers its whole module graph, which
        # also registers every Feature / LiveQuery / VolumeProvider subclass we
        # need to walk below.
        import siibra.features as features_pkg
        from siibra.configuration.configuration import Configuration
        from siibra.core.parcellation import Parcellation
        from siibra.core.region import Region
        from siibra.features.anchor import AnatomicalAnchor
        from siibra.features.feature import Feature
        from siibra.livequeries.query import LiveQuery
        from siibra.locations.location import Location
        from siibra.retrieval.repositories import RepositoryConnector
        from siibra.retrieval.requests import HttpRequest
        from siibra.volumes.parcellationmap import Map
        from siibra.volumes.volume import Volume, VolumeProvider

        self._instrument_feature_match(Feature, features_pkg, detailed)

        span = self._span_wrapper
        count = self._set_count

        # --- feature discovery -------------------------------------------------
        def get_instances_attrs(cls, args, kwargs):
            return {
                "siibra.feature_type": _type_name(cls),
                "siibra.cache_hit": getattr(cls, "_preconfigured_instances", None) is not None,
            }

        self._wrap(Feature, "get_instances", span("siibra.Feature.get_instances", get_instances_attrs, count))
        self._wrap(Feature, "livequery", span(
            "siibra.Feature.livequery",
            lambda cls, a, k: {"siibra.feature_type": _type_name(cls), **_concept_attrs(_arg(a, k, 0, "concept"))},
            count,
        ))
        self._wrap(Feature, "get_instance_by_id", span(
            "siibra.Feature.get_instance_by_id",
            lambda cls, a, k: {"siibra.feature.id": str(_arg(a, k, 0, "feature_id"))},
        ))
        self._wrap_hierarchy(LiveQuery, "query", span(
            "siibra.LiveQuery.query",
            lambda q, a, k: {
                "siibra.livequery": _type_name(q),
                "siibra.feature_type": _type_name(getattr(q, "feature_type", None)),
                "siibra.livequery.args": sorted(getattr(q, "_kwargs", {}) or {}),
                **_concept_attrs(_arg(a, k, 0, "concept")),
            },
            count,
        ))
        self._wrap(Configuration, "build_objects", span(
            "siibra.Configuration.build_objects",
            lambda conf, a, k: {"siibra.config.folder": str(_arg(a, k, 0, "folder"))},
            count,
        ))

        # --- anatomical matching ----------------------------------------------
        # Recursive over the region tree; dedupe keeps only the outermost call.
        self._wrap(AnatomicalAnchor, "match_location_to_region", span(
            "siibra.AnatomicalAnchor.match_location_to_region",
            lambda cls, a, k: {
                "siibra.location.type": _type_name(_arg(a, k, 0, "location")),
                "siibra.location.space": _space_name(getattr(_arg(a, k, 0, "location"), "space", None)),
                "siibra.region.name": str(getattr(_arg(a, k, 1, "region"), "name", "")),
            },
            lambda s, r, i: s.set_attribute("siibra.match.qualification", str(getattr(r, "qualification", None))),
        ))
        self._wrap_hierarchy(Location, "warp", span(
            "siibra.Location.warp",
            lambda loc, a, k: {
                "siibra.location.type": _type_name(loc),
                "siibra.space.source": _space_name(getattr(loc, "space", None)),
                "siibra.space.target": _space_name(_arg(a, k, 0, "space")),
            },
        ))

        # --- maps & volumes ----------------------------------------------------
        self._wrap(Region, "fetch_regional_map", span(
            "siibra.Region.fetch_regional_map",
            lambda r, a, k: {
                "siibra.region.name": str(r.name),
                "siibra.space": _space_name(_arg(a, k, 0, "space")),
                "siibra.maptype": str(_arg(a, k, 1, "maptype", "")),
            },
        ))
        self._wrap(Region, "compute_centroids", span(
            "siibra.Region.compute_centroids",
            lambda r, a, k: {"siibra.region.name": str(r.name), "siibra.space": _space_name(_arg(a, k, 0, "space"))},
        ))
        self._wrap(Parcellation, "get_map", span(
            "siibra.Parcellation.get_map",
            lambda p, a, k: {
                "siibra.parcellation.name": str(p.name),
                "siibra.space": _space_name(_arg(a, k, 0, "space")),
                "siibra.maptype": str(_arg(a, k, 1, "maptype", "")),
            },
        ))
        map_attrs = lambda m, a, k: {  # noqa: E731
            "siibra.map.type": _type_name(m),
            "siibra.map.name": str(getattr(m, "name", "")),
            "siibra.space": _space_name(getattr(m, "space", None)),
        }
        for attr in ("fetch", "assign", "compute_centroids"):
            on_result = count if attr == "assign" else None
            self._wrap_hierarchy(Map, attr, span(f"siibra.Map.{attr}", map_attrs, on_result))
        self._wrap_hierarchy(Volume, "fetch", span(
            "siibra.Volume.fetch",
            lambda v, a, k: {
                "siibra.volume.type": _type_name(v),
                "siibra.volume.name": str(getattr(v, "name", "")),
                "siibra.volume.format": str(_arg(a, k, 0, "format", "")),
            },
        ))
        self._wrap_hierarchy(VolumeProvider, "fetch", span(
            "siibra.VolumeProvider.fetch",
            lambda p, a, k: {"siibra.volume.srctype": str(getattr(p, "srctype", _type_name(p)))},
        ))

        # --- data retrieval ----------------------------------------------------
        def http_attrs(req, a, k):
            attrs = {"siibra.request.type": _type_name(req)}
            url = getattr(req, "url", None)
            if url:
                attrs["url.full"] = str(url)
            cached = _safe(lambda: req.cached and not req.refresh)
            if cached is not None:
                attrs["siibra.cache_hit"] = bool(cached)
            return attrs

        self._wrap_hierarchy(HttpRequest, "get", span("siibra.HttpRequest.get", http_attrs))
        self._wrap_hierarchy(RepositoryConnector, "get", span(
            "siibra.RepositoryConnector.get",
            lambda c, a, k: {
                "siibra.connector.type": _type_name(c),
                "siibra.connector.filename": str(_arg(a, k, 0, "filename")),
                "siibra.connector.folder": str(_arg(a, k, 1, "folder", "")),
            },
        ))

        # --- feature payload loading ------------------------------------------
        def load_matrix_attrs(f, a, k):
            return {"siibra.feature_type": _type_name(f), "siibra.subject": str(_arg(a, k, 0, "subject"))}

        for modpath, clsname in (
            ("siibra.features.connectivity.regional_connectivity", "RegionalConnectivity"),
            ("siibra.features.tabular.interareal_connectivity", "InterarealConnectivityMatrix"),
        ):
            cls = _safe(lambda: getattr(__import__(modpath, fromlist=[clsname]), clsname))
            if cls is not None:
                self._wrap_hierarchy(cls, "_load_matrix", span("siibra.Feature.load_matrix", load_matrix_attrs))

        loader = _safe(lambda: __import__("siibra.livequeries.bigbrain", fromlist=["x"]).WagstylProfileLoader)
        if loader is not None:
            self._wrap(loader, "_load", span("siibra.WagstylProfileLoader.load"))

        # --- fine-grained (opt-in): one span per feature / region decode -----------
        if detailed:
            self._wrap(Parcellation, "find_regions", span(
                "siibra.Parcellation.find_regions",
                lambda _, a, k: {"siibra.region.spec": str(_arg(a, k, 0, "region_spec"))},
                count,
                dedupe_on_owner=False,
            ))

    def _instrument_feature_match(self, Feature, features_pkg, detailed: bool):
        tracer = self._tracer

        def match_wrapper(wrapped, cls, args, kwargs):
            if not is_instrumentation_enabled():
                return wrapped(*args, **kwargs)
            concept = _arg(args, kwargs, 0, "concept")
            feature_type = _arg(args, kwargs, 1, "feature_type")
            resolved = isinstance(feature_type, type)

            # Feature.match recurses list -> str -> class. Emit one span for the
            # user's call plus one child span per concrete feature class.
            if not resolved and ("match", "outer") in _ACTIVE.get():
                return wrapped(*args, **kwargs)

            attributes = dict(_safe(_concept_attrs, concept, default={}))
            if resolved:
                attributes["siibra.feature_type"] = feature_type.__name__
            elif isinstance(feature_type, list):
                attributes["siibra.feature_type.query"] = [_type_name(t) if isinstance(t, type) else str(t)
                                                           for t in feature_type]
            else:
                attributes["siibra.feature_type.query"] = str(feature_type)
            if kwargs:
                extra = sorted(k for k in kwargs if k not in ("concept", "feature_type"))
                if extra:
                    attributes["siibra.match.kwargs"] = extra

            with tracer.start_as_current_span("siibra.Feature.match", attributes=attributes) as span:
                if not resolved:
                    with _dedupe(("match", "outer")):
                        result = wrapped(*args, **kwargs)
                    if span.is_recording():
                        self._set_count(span, result)
                    return result

                stats = {"candidates": 0, "hits": 0}
                token = _MATCH_STATS.set(stats)
                try:
                    result = wrapped(*args, **kwargs)
                finally:
                    _MATCH_STATS.reset(token)
                if span.is_recording():
                    span.set_attribute("siibra.match.candidates", stats["candidates"])
                    span.set_attribute("siibra.match.preconfigured_hits", stats["hits"])
                    self._set_count(span, result)
                return result

        def matches_wrapper(wrapped, feature, args, kwargs):
            stats = _MATCH_STATS.get()
            if not detailed or not is_instrumentation_enabled():
                result = wrapped(*args, **kwargs)
            else:
                with tracer.start_as_current_span(
                    "siibra.Feature.matches",
                    attributes={"siibra.feature_type": _type_name(feature),
                                "siibra.feature.id": str(_safe(lambda: feature.id, default=""))},
                ) as span:
                    result = wrapped(*args, **kwargs)
                    span.set_attribute("siibra.match.hit", bool(result))
            if stats is not None:
                stats["candidates"] += 1
                stats["hits"] += int(bool(result))
            return result

        self._wrap(Feature, "match", match_wrapper)
        self._wrap(Feature, "matches", matches_wrapper)

        # `siibra.features.get = Feature.match` was bound at import time and still
        # points at the unpatched classmethod: rebind it.
        type(self)._features_get_original = features_pkg.get
        features_pkg.get = Feature.match

    # ------------------------------------------------------------ uninstrument

    def _uninstrument(self, **kwargs):
        if self._features_get_original is not None:
            import siibra.features as features_pkg

            features_pkg.get = self._features_get_original
            type(self)._features_get_original = None
        for owner, attr in reversed(self._patched):
            # Restore the raw descriptor from the class __dict__. Going through
            # getattr() (as opentelemetry's unwrap() does) would put back a
            # *bound* classmethod and break every subclass.
            current = vars(owner).get(attr)
            if isinstance(current, wrapt.FunctionWrapper):
                setattr(owner, attr, current.__wrapped__)
        self._patched.clear()
