FROM docker-registry.ebrains.eu/siibra/siibra-python:v2.0.0a0

COPY ./requirements /requirements
RUN python -m pip install -r /requirements/v4-worker.txt 

COPY . /worker
WORKDIR /worker

RUN chown -R nobody /worker
USER nobody

ENV SIIBRA_API_ROLE=worker

HEALTHCHECK --interval=60s --timeout=10s --start-period=120s --retries=3 \
    CMD [ "python", "worker_health_v4.py" ]

ENTRYPOINT celery -A new_api.worker.app worker -l WARNING -O fair
