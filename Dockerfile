# Use fastapi python 3.7 as base image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Upgrade pip to latest version
RUN python -m pip install --upgrade pip

# Copy the application and install dependencies
COPY . /app
WORKDIR /app

RUN python -m pip install -r app/requirements.txt
RUN python -m pip install anytree
RUN python -m pip install pillow
RUN python -m pip install scikit-image

# Create directory for cache and set an environment variable for siibra
RUN mkdir -p cache
RUN chmod 777 cache
RUN chmod 777 /app
ENV SIIBRA_CACHEDIR=/app/cache

# Expose port
EXPOSE 5000

# Start application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
