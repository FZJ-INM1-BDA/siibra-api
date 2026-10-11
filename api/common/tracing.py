"""Optional OpenTelemetry tracing helpers.

Tracing is an optional observability concern: in deployments the worker/server
run under `opentelemetry-instrument`, but the package may be absent in local
dev, tests, or minimal installs. If `opentelemetry` cannot be imported, these
helpers fall back to no-ops so application behaviour is unchanged.

Usage:
    from api.common.tracing import get_tracer
    tracer = get_tracer(__name__)

    with tracer.start_as_current_span("do_work") as span:
        span.set_attribute("key", "value")
        ...
"""
from contextlib import contextmanager

try:
    from opentelemetry import trace as _trace

    def get_tracer(name: str):
        # Returns a real tracer. Note: even without a configured TracerProvider
        # this yields a no-op tracer, so it is safe when otel is installed but
        # not instrumented.
        return _trace.get_tracer(name)

except ImportError:

    class _NoopSpan:
        """Mimics the subset of the OTel Span API used in this codebase."""

        def set_attribute(self, *args, **kwargs):
            pass

        def set_attributes(self, *args, **kwargs):
            pass

        def record_exception(self, *args, **kwargs):
            pass

        def set_status(self, *args, **kwargs):
            pass

        def add_event(self, *args, **kwargs):
            pass

    class _NoopTracer:
        @contextmanager
        def start_as_current_span(self, name, *args, **kwargs):
            yield _NoopSpan()

    _NOOP_TRACER = _NoopTracer()

    def get_tracer(name: str):
        return _NOOP_TRACER
