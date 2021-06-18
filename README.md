<p align="center">
    <img src="statuc/images/siibra-api.jpeg" width="600">
</p>

# siibra - API 

*Authors: Big Data Analytics Group, Institute of Neuroscience and Medicine (INM-1), Forschungszentrum Jülich GmbH*

Copyright 2020-2021, Forschungszentrum Jülich GmbH

> :warning: **`siibra-api` is still at an experimental stage.** The API of the library is not
stable, and the software is not yet fully tested. You are welcome to install and
test it, but be aware that you will likely encounter bugs.

## Overview

Siibra-API provides an easy REST access to the siibra-python features.

The main goal is to abstract the python functionalities in a way that they can be used via HTTP and make it more independent and accessible.

## Documentation

coming soon

## Usage examples

A list of all API endpoints and a playground to directly test it can be found here:

[Swagger API](https://siibra-api.apps-dev.hbp.eu/v1_0/docs#/)

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


## Acknowledgements

This software code is funded from the European Union’s Horizon 2020 Framework
Programme for Research and Innovation under the Specific Grant Agreement No.
945539 (Human Brain Project SGA3).
