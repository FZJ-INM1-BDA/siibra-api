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

## Local Startup / Development


The siibra-api can be easily started locally with docker compose.
A `docker-compose.yml` file is already included in the project. 
Only some environment variables are needed. This variables can be defined in a file `.env`.

Step by step start up:

1. Create `.env` file on the same level as `docker-compose.yml`
2. Add all needed environment variables as described in the example:

``` 
SIIBRA_ENVIRONMENT=DEVELOPMENT
EBRAINS_IAM_CLIENT_ID=<IAM_CLIENT_ID>
EBRAINS_IAM_CLIENT_SECRET=<IAM_CLIENT_SECRET>
EBRAINS_IAM_REFRESH_TOKEN=<IAM_REFRESH_TOKEN>
```

3. Run `docker-compose --env-file ./.env.dev -f docker-compose.yml -f docker-compose-dev.yml up -d` to start the application

:bulb: 

Running the application with docker-compose allows **hot reload**.
Changes in the code will be directly taken over into the running container. 


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
