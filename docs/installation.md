## From docker/docker-compose

To install docker, consult the [official documentation](https://www.docker.com/).

```bash
# available version(s)
# To see an up to date list, go to https://docker-registry.ebrains.eu/harbor/projects/28/repositories/siibra-api
export SIIBRA_API_IMAGE_VERSION="latest" || "0.3" || "0.3.11"

# Pull the all-in-one image from docker registry
docker pull docker-registry.ebrains.eu/siibra/siibra-api:${SIIBRA_API_IMAGE_VERSION}

# To pull the server image from docker registery
# docker pull docker-registry.ebrains.eu/siibra/siibra-api:${SIIBRA_API_IMAGE_VERSION}-server

# To pull the server image from docker registery
# docker pull docker-registry.ebrains.eu/siibra/siibra-api:${SIIBRA_API_IMAGE_VERSION}-server
```

## From source

```bash

# clone the project

git clone https://github.com/FZJ-INM1-BDA/siibra-api.git

# cd into the directory 

cd siibra-api

# install dependencies for all-in-one configuration
pip install -r requirements/all.txt

# To install dependencies for server in a server-worker configuration
# pip install -r requirements/server.txt

# To install dependencies for worker in a server-worker configuration
# pip install -r requirements/worker.txt

```

## (Optional) Redis

[Do I need redis?](requirements.md#optional)

```bash
# Pull latest redis
docker pull redis:latest
```

## (Optional) Shared docker volume

!!! note
    As `docker-compose` configures the shared volume in the yml file, this step should be skipped if siibra-api is run via docker-compose.

Shared docker volume is required if siibra-api is run via docker, and uses [server-worker](architecture.throughput.md#server-worker) configuration.

```bash
docker volume create siibra_api_shared_vol
```
