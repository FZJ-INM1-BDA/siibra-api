# Use fastapi python 3.7 as base image
FROM python:3.7

# Upgrade pip to latest version
RUN python -m pip install --upgrade pip

# Copy and install common dependencies
# This should allow *some* layers to be cached
COPY ./requirements /requirements
WORKDIR /requirements
RUN python -m pip install -r common.txt

# can be passed in via --build-arg DEV_FLAG=1
ARG DEV_FLAG
# if DEV_FLAG flag is set, set DEPLOY_ENVIRONMENT=develop
ENV DEPLOY_ENVIRONMENT=${DEV_FLAG:+develop}
# if DEPLOY_ENVIRONMENT is not yet set, set it to production
ENV DEPLOY_ENVIRONMENT=${DEPLOY_ENVIRONMENT:-production}
# if DEV_FLAG flag is set, set SIIBRA_CONFIG_GITLAB_PROJECT_TAG=develop
#ENV SIIBRA_CONFIG_GITLAB_PROJECT_TAG=${DEV_FLAG:+develop}

COPY . /app
WORKDIR /app

RUN if [ "$DEPLOY_ENVIRONMENT" = "production" ]; \
  then python -m pip install -r requirements/prod.txt; \
  else python -m pip install -r requirements/dev.txt; \
  fi


# Create directory for cache and set an environment variable for siibra
RUN mkdir -p /tmp/.siibra-cache
RUN chmod 777 /tmp/.siibra-cache
RUN chmod 777 /app
ENV SIIBRA_CACHEDIR=/tmp/.siibra-cache

RUN chown -R nobody /app
USER nobody

# Expose port
EXPOSE 5000

# Start application
# SIIBRA_CONFIG_GITLAB_PROJECT_TAG will be set to empty string if DEV_FLAG build arg is unset
# It needs to be unset, in this case, or the empty string will be parsed as truthy in python
ENTRYPOINT ["/bin/bash", "-c", "if [ -z $SIIBRA_CONFIG_GITLAB_PROJECT_TAG ]; then unset SIIBRA_CONFIG_GITLAB_PROJECT_TAG; fi && uvicorn app.app:app --host 0.0.0.0 --port 5000 --workers 4"]
