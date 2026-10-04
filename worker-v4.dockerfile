FROM docker-registry.ebrains.eu/siibra/siibra-python:v2.0.0a4

COPY ./requirements /requirements
RUN python -m pip install -r /requirements/v4-worker.txt
RUN opentelemetry-bootstrap -a install

COPY . /worker
WORKDIR /worker

RUN chown -R nobody /worker
USER nobody

ENV SIIBRA_API_ROLE=worker

# --- OpenTelemetry trace forwarding ---------------------------------------
# These are consumed by `opentelemetry-instrument` (see ENTRYPOINT below).
# Override at runtime (docker run -e / compose environment:) to ship traces
# to your collector. Defaults disable exporting so the image is inert unless
# explicitly configured.
#
# Name shown in the backend for traces from this service.
ENV OTEL_SERVICE_NAME=siibra-api-worker-v4
# Extra resource attributes (OTel's equivalent of Prometheus labels) attached
# to every span. Override during deployment with real values.
ENV OTEL_RESOURCE_ATTRIBUTES=service.deployment=default,service.version=myversion
# Exporter to use for traces. Set to `otlp` to forward, `none` to disable.
ENV OTEL_TRACES_EXPORTER=none
# OTLP transport: `grpc` (usually :4317) or `http/protobuf` (usually :4318).
ENV OTEL_EXPORTER_OTLP_PROTOCOL=grpc
# Collector endpoint, e.g. http://otel-collector:4317
# ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
# Per-signal endpoint override (takes precedence over the one above).
# ENV OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://otel-collector:4317/v1/traces
# Extra headers for the exporter, e.g. auth tokens (comma-separated key=value).
# ENV OTEL_EXPORTER_OTLP_HEADERS=authorization=Bearer%20<token>
# ---------------------------------------------------------------------------

HEALTHCHECK --interval=60s --timeout=10s --start-period=120s --retries=3 \
    CMD [ "python", "worker_health_v4.py" ]

ENTRYPOINT ["opentelemetry-instrument", "celery", "-A", "new_api.worker.app", "worker", "-l", "WARNING", "-O", "fair"]
