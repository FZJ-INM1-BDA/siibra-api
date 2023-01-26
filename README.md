<p align="center">
    <img src="static/images/siibra-api.jpeg" width="600">
</p>

# siibra - API 

Copyright 2020-2021, Forschungszentrum Jülich GmbH

*Authors: Big Data Analytics Group, Institute of Neuroscience and Medicine (INM-1), Forschungszentrum Jülich GmbH*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


> :warning: **`siibra-api` is still at an experimental stage.** The API of the library is not
stable, and the software is not yet fully tested. You are welcome to install and
test it, but be aware that you will likely encounter bugs.

## Overview

Siibra-API provides an easy REST access to the siibra-python features.

The main goal is to abstract the python functionalities in a way that they can be used via HTTP and make it more independent and accessible.

## Documentation

The documentation of the api and all endpoints is done by swagger.

In addition to the documentation of each API endpoint, a playground is provided for direct testing.

[Swagger API](https://siibra-api-stable.apps.hbp.eu/v1_0/docs#/)

## Configuration

siibra-api can be configured by:

- environment variables, as indicated by the <./api/siibra_api_config.py> , or ...
- directly overwriting the <./api/siibra_api_config.py> file, by overwriting or docker volume mounting

## Architecture

siibra-api is configured to run in three different modes: `all` , `server` and `worker`, set via the `ROLE` variable in <./api/siibra_api_config.py> .

siibra-api will behave differently baesd on the role it is assigned. As a result, each role requires different dependencies, and different `dockerfile`s:


| role | dependency | dockerfile | handle http | data processing |
| --- | --- | --- | --- | --- |
| `all` | <./requirements/all.txt> | <./Dockerfile> | ✓ | ✓ |
| `server` | <./requirements/server.txt> | <./server.dockerfile> | ✓ | |
| `worker` | <./requirements/worker.txt> | <./worker.dockerfile> | | ✓ | 



## Local Startup

siibra-api can be run locally with python >= 3.7, or docker-compose.

### with python >= 3.7

```sh
pip install -r requirements/all.txt && uvicorn api.server:api --host 127.0.0.1 --port 5000
```

### with `docker-compose`

```sh
docker-compose -f ./docker-compose.yml up -d
```

### server/worker configuration

A `docker-compose` script is also provided for server/worker configuration:

```sh
docker-compose -f ./docker-compose-sw.yml up-d
```


## Development

siibra-api can be launched with hot-reload enabled. Changes to the code will automatically restart the services.

### with python >= 3.7

```sh
pip install -r requirements/all.txt && uvicorn api.server:api --host 127.0.0.1 --port 5000 --reload
```

### with `docker-compose`

```sh
docker-compose -f ./docker-compose-dev.yml up -d
```

## How to contribute

If you want to contribute to ``siibra-api``, feel free to fork it and open a
pull request with your changes. You are also welcome to contribute to
discussion in the issue tracker and of course to report issues you are
facing yourself. If you find the software useful, please reference this
repository URL in publications and derived work. You can also star the
project to show us that you are using it.

## Acknowledgements

This software code is funded from the European Union’s Horizon 2020 Framework
Programme for Research and Innovation under the Specific Grant Agreement No.
945539 (Human Brain Project SGA3).
