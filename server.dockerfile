FROM python:3.11-slim

ARG GIT_HASH
ENV GIT_HASH=${GIT_HASH:-unknown-hash}

RUN python -m pip install -U pip
COPY ./requirements /requirements
RUN python -m pip install -r /requirements/server.txt
RUN opentelemetry-bootstrap -a install
# in uv, run 
# uv pip install $(venv/bin/opentelemetry-bootstrap)
# instead

COPY . /api
WORKDIR /api

RUN chown -R nobody /api
USER nobody

EXPOSE 5000

ENV SIIBRA_API_ROLE=server

# --- OpenTelemetry trace forwarding ---------------------------------------
# These are consumed by `opentelemetry-instrument` (see ENTRYPOINT below).
# Override at runtime (docker run -e / compose environment:) to ship traces
# to your collector. Defaults disable exporting so the image is inert unless
# explicitly configured.
#
# Name shown in the backend for traces from this service.
ENV OTEL_SERVICE_NAME=siibra-api-server
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

HEALTHCHECK --start-period=10s --timeout=3s --retries=3 \
    CMD [ "python", "server_health.py" ]

ENTRYPOINT ["opentelemetry-instrument", "uvicorn", "api.server:api", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
