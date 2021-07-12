# Use fastapi python 3.7 as base image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Upgrade pip to latest version
RUN python -m pip install --upgrade pip

# Copy the application and install dependencies
COPY . /app
WORKDIR /app

RUN python -m pip install -U pip

# can be passed in via --build-arg PROD_FLAG=1
ARG PROD_FLAG
# if prod flag is set, set DEPLOY_ENVIRONMENT=production
ENV DEPLOY_ENVIRONMENT=${PROD_FLAG:+production}
# if prod flag is NOT set, set SIIBRA_CONFIG_GITLAB_PROJECT_TAG=develop
ENV SIIBRA_CONFIG_GITLAB_PROJECT_TAG=${PROD_FLAG:-develop}

RUN if [ "$DEPLOY_ENVIRONMENT" = "production" ]; \
  then python -m pip install -r requirements/prod.txt; \
  else python -m pip install -r requirements/dev.txt; \
  fi

RUN python -m pip install anytree
RUN python -m pip install pillow
RUN python -m pip install scikit-image

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
ENTRYPOINT ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5000"]
