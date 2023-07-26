siibra-api can be launched with hot-reload enabled. Changes to the code will automatically restart the service.

## Requirements

To develop siibra-api locally, you will need:

- git
- python 3.7+ or docker

## With python

```sh
# disable caching
export CI=1

# install requirements
pip install -r requirements/all.txt

# start server with hot reload
uvicorn api.server:api --host 127.0.0.1 --port 5000 --reload
```

## With docker-compose
```sh
docker-compose -f ./docker-compose-dev.yml up
```
