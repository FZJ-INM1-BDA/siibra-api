## (Optional) Redis 

[Do I need redis?](requirements.md#optional)

```bash
# start redis container
docker run -it --rm --name "redis" -p "6379:6379" redis:latest
```

## [all-in-one configuration](architecture.throughput.md#all-in-one)

### From docker-compose

```bash
export SIIBRA_API_IMAGE_VERSION="latest" || "0.3" || "0.3.11"
echo "SIIBRA_API_IMAGE_VERSION=$SIIBRA_API_IMAGE_VERSION" > .siibra-docker-compose.env

docker-compose --env-file .siibra-docker-compose.env -f docker-compose.yml up
```

### From docker

```bash

export SIIBRA_API_IMAGE_VERSION="latest" || "0.3" || "0.3.11"

# If use without redis
docker run -it \
    --rm \
    --name "siibra-api-all" \
    --env CI=1 \
    -p "5000:5000" \
    docker-registry.ebrains.eu/siibra/siibra-api:${SIIBRA_API_IMAGE_VERSION}

# If use with redis
# docker run -it \
#     --rm \
#     --name "siibra-api-all" \
#     --env SIIBRA_API_REDIS_HOST=redis \
#     --link redis \
#     -p "5000:5000" \
#     docker-registry.ebrains.eu/siibra/siibra-api:${SIIBRA_API_IMAGE_VERSION}

```

### From source

```bash

# If use without redis
export CI=1

# If using with redis
# unset CI

# By default, if SIIBRA_API_ROLE is unset, 'all' is the fallback value
# export SIIBRA_API_ROLE=all
uvicorn api.server.api
```

## [server-worker configuration](architecture.throughput.md#server-worker)

### From docker-compose

```bash
export SIIBRA_API_IMAGE_VERSION="latest" || "0.3" || "0.3.11"
echo "SIIBRA_API_IMAGE_VERSION=$SIIBRA_API_IMAGE_VERSION" > .siibra-docker-compose.env

docker-compose --env-file .siibra-docker-compose.env -f docker-compose-sw.yml up
```

### From docker

server:

```bash
export SIIBRA_API_IMAGE_VERSION="latest" || "0.3" || "0.3.11"

docker run -it \
    --rm \
    --name "siibra-api-server" \
    --env SIIBRA_API_REDIS_HOST=redis \
    --env SIIBRA_CACHEDIR=/persist_shared_vol \
    --volume siibra_api_shared_vol:/persist_shared_vol \
    --link redis \
    -p "5000:5000" \
    docker-registry.ebrains.eu/siibra/siibra-api:${SIIBRA_API_IMAGE_VERSION}-server
```

worker(s): (feel free to spawn as many instance as resource allows/you wish)

```bash
export SIIBRA_API_IMAGE_VERSION="latest" || "0.3" || "0.3.11"

docker run -it \
    --rm \
    --name "siibra-api-server" \
    --env SIIBRA_API_REDIS_HOST=redis \
    --env SIIBRA_CACHEDIR=/persist_shared_vol \
    --volume siibra_api_shared_vol:/persist_shared_vol \
    --link redis \
    -p "5000:5000" \
    docker-registry.ebrains.eu/siibra/siibra-api:${SIIBRA_API_IMAGE_VERSION}-worker
```

### From source

server:

```bash
export SIIBRA_API_ROLE=server
uvicorn api.server.api
```

worker(s): (feel free to spawn as many instance as resource allows/you wish)

```bash
export SIIBRA_API_ROLE=worker
# listen on all queues by:
celery -A api.worker.app worker -l INFO
# or listen to specific queues by:
# celery -A api.worker.app worker -l INFO -Q 0.3.11.siibraapilatest.core
```
