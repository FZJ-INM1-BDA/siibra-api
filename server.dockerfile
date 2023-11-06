FROM python:3.10-alpine

ARG GIT_HASH
ENV GIT_HASH=${GIT_HASH:-unknown-hash}

RUN python -m pip install -U pip
COPY ./requirements /requirements
RUN python -m pip install -r /requirements/server.txt

COPY . /api
WORKDIR /api

RUN chown -R nobody /api
USER nobody

EXPOSE 5000

ENV SIIBRA_API_ROLE=server

HEALTHCHECK --start-period=10s --timeout=3s --retries=3 \
    CMD [ "python", "server_health.py" ]

ENTRYPOINT uvicorn api.server:api --host 0.0.0.0 --port 5000 --workers 4
