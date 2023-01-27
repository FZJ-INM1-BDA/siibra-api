FROM python:3.10
RUN python -m pip install -U pip
COPY ./requirements/all.txt /requirements.txt
RUN python -m pip install -r /requirements.txt

COPY . /api
WORKDIR /api

RUN chown -R nobody /api
USER nobody

EXPOSE 5000

ENV SIIBRA_API_ROLE=all

ENTRYPOINT uvicorn api.server:api --host 0.0.0.0 --port 5000 --workers 4
