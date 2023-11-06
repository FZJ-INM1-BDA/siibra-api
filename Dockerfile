FROM python:3.10

ARG GIT_HASH
ENV GIT_HASH=${GIT_HASH:-unknown-hash}

RUN python -m pip install -U pip
COPY ./requirements /requirements
RUN python -m pip install -r /requirements/all.txt

COPY . /api
WORKDIR /api

RUN chown -R nobody /api
USER nobody

EXPOSE 5000

HEALTHCHECK --start-period=120s --timeout=3s \
    CMD curl http://localhost:5000/v3_0/atlases || exit 1

ENV SIIBRA_API_ROLE=all

ENTRYPOINT uvicorn api.server:api --host 0.0.0.0 --port 5000 --workers 4
