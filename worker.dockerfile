FROM python:3.10
RUN python -m pip install -U pip
COPY ./requirements /requirements
RUN python -m pip install -r /requirements/worker.txt

COPY . /worker
WORKDIR /worker

RUN chown -R nobody /worker
USER nobody

ENV SIIBRA_API_ROLE=worker

HEALTHCHECK --interval=60s --timeout=10s --start-period=120s --retries=3 \
    CMD [ "python", "worker_health.py" ]

ENTRYPOINT celery -A api.worker.app worker -l INFO
