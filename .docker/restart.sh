#! /bin/bash

git -C ./siibra-configuration fetch && git -C ./siibra-configuration merge --ff-only origin/master

docker pull docker-registry.ebrains.eu/siibra/siibra-api:latest
docker pull docker-registry.ebrains.eu/siibra/siibra-explorer:staging

docker-compose down
sleep 5
docker-compose up -d