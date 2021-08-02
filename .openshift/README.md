# Deployment documentation

This document outlines the deployment of `siibra-api` on EBRAINS infrastructure.

## Overview

`siibra-api` are continuously deployed on openshift container platform hosted by EBRAINS.

The continuous deployment of `siibra-api` involves the following steps:

- building docker image
- tag the image, and push to registry
- pull and run the newly built image

## Build

This section outlines the procedure of continuously building and archiving docker images of `siibra-api`.

### Images

Docker images are built with [`Dockerfile`](../Dockerfile) by github action withs [yml spec](../.github/workflows/docker-img.yml), and pushed to EBRAINS docker image registry at docker-registry.ebrains.eu

`docker-registry.ebrains.eu` is set as the registry

`siibra` is set as the namespace

`siibra-api` is set as the image name

The built image will be tagged with one of the three tags depending on the trigger condition.

| tag | trigger condition |
| --- | --- |
| latest | push to `master` branch |
| rc | release name include the string `rc` |
| stable | all other releases |

The built image will be tagged as:

`docker-registry.ebrains.eu/siibra/siibra-api:{latest|rc|stable}`

### Registry

The built docker image will then be pushed to `docker-registry.ebrains.eu` with the access token of a bot account with the rights to push image in `siibra` namespace.

The login credentials are stored in github action secrets:

- username: `secrets.EBRAINS_DOCKER_REG_USER`
- access token: `secrets.EBRAINS_DOCKER_REG_TOKEN`

> :warning: There are currently no mechanism to delete artefacts from `docker-registry.ebrains.eu`. One must periodically, manually delete untagged images to avoid filling of allotted diskspace.

---

// TODO setup retention policy to allow automatic deletion of artefacts

---

## Deployment

This section outlines how the built image are deployed.

> :info: Previous internal guides described a combination of s2i with docker build strategy. This has been demonstrated to be both slow (at build time) and unreliable (over the deployment lifetime).

### Variables

| name | value | 
| --- | --- |
| `PROJECT_NAME` | `siibra-api` |
| `OKD_ENDPOINT` (prod) | `https://okd.hbp.eu:443` |
| `OKD_ENDPOINT` (dev) | `https://okd-dev.hbp.eu:443` |
| `OKD_SECRET` (prod) | `{{ secrets.OKD_PROD_SECRET }}` (stored in github action secrets) |
| `OKD_SECRET` (dev) | `{{ secrets.OKD_DEV_SECRET }}` (stored in github action secrets) |


### Triggering deployment

Deployments resides in [docker-img.yml](../.github/workflows/docker-img.yml), `job['deploy-on-okd']`. The steps are summarised as below:

- determine if targeting prod or dev cluster.

  - If the trigger is update of `master` branch, target dev cluster

  - If the trigger is release, target prod cluster

- login to openshift container platform with the command

  ```bash
  oc login ${OKD_ENDPOINT} --token ${OKD_SECRET}
  ```

- checkout project `siibra-api` with the command

  ```bash
  oc project ${PROJECT_NAME}
  ```

- check if deployment with name `siibra-api-branch-deploy-${DEPLOY_FLAVOUR}` exists
  - if exists, rollout latest deployment with the command 
  
    ```bash
    oc rollout latest dc/siibra-api-branch-deploy-${DEPLOY_FLAVOUR}
    ```

  - if does not exist, create new deployment with name `siibra-api-branch-deploy-${DEPLOY_FLAVOUR}`, using deployment template[2] with corresponding parameters[3]

### [1] OKD service accounts



### [2] Deployment template

An [openshift template](./branch-deploy-template.yml) has been added to both production (https://okd.hbp.eu) and develop (https://okd-dev.hbp.eu) clusters.

This is done ahead of any deploys, is valid for all future deploys and rarely needs to be updated.

---

// TODO The process of adding/editing template is fragile and error prone. We should figure out a long term solution, or be vigilant and update the template as little as possible

---

### [3] Deployment parameters

Per [deployment template](./branch-deploy-template.html), a number of parameters may be required when creating new deployments.

| name | required | desc | 
| --- | --- | --- |
| `SESSION_SECRET` | | Random strings to encrypt sessions. Not currently used. |
| `DOCKER_IMAGE_TAG` | true | Dictates which image tag to pull. Currently, possible values are `{latest\|rc\|stable}`. |
| `DEPLOY_FLAVOUR` | true | Acts similar to deploy ID. Distinguishes one deployment from another. Currently, possible values are `{latest\|rc\|stable}`. Also affects routes: `siibra-api-{DEPLOY_FLAVOUR}.apps{DEPLOY_SITE_POSTFIX}.hbp.eu` |
| `DEPLOY_SITE_POSTFIX` | | Dictates if postfix, if any, should be added to the route: `siibra-api-{DEPLOY_FLAVOUR}.apps{DEPLOY_SITE_POSTFIX}.hbp.eu`. Defaults to `''` (empty string). Possible value: `-dev`|
