# Use fastapi python 3.7 as base image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Upgrade pip to latest version
RUN python -m pip install --upgrade pip

# Copy the application and install dependencies
COPY . /app
WORKDIR /app

RUN python -m pip install -U pip

RUN if [ "$DEPLOY_ENVIRONMENT" = "production" ] ; then python -m pip install -r requirements/prod.txt ; else python -m pip install -r requirements/dev.txt ; fi
RUN python -m pip install anytree
RUN python -m pip install pillow
RUN python -m pip install scikit-image

# Create directory for cache and set an environment variable for siibra
RUN mkdir -p cache
RUN chmod 777 cache
RUN chmod 777 /app
ENV SIIBRA_CACHEDIR=/app/cache

RUN chown -R nobody /app
USER nobody

# Expose port
EXPOSE 5000

# Start application
ENTRYPOINT ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5000"]
