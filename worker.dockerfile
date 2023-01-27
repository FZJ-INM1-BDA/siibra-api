FROM python:3.10
RUN python -m pip install -U pip
COPY ./requirements/worker.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /worker
WORKDIR /worker

RUN chown -R nobody /worker
USER nobody

ENV SIIBRA_API_ROLE=worker

ENTRYPOINT celery -A api.worker.app worker -l INFO
