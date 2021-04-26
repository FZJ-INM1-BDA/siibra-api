# Use fastapi python 3.7 as base image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Upgrade pip to latest version
RUN python -m pip install --upgrade pip

# Copy the application and install dependencies
COPY . /app
WORKDIR /app

RUN python -m pip install -U pip

RUN git clone -b feat_addVolsrc https://github.com/FZJ-INM1-BDA/siibra-python.git
RUN cd siibra-python && python -m pip install .

RUN python -m pip install -r app/requirements.txt
RUN python -m pip install anytree
RUN python -m pip install pillow
RUN python -m pip install scikit-image

# Create directory for cache and set an environment variable for siibra
RUN mkdir cache
RUN chmod 777 cache
RUN chmod 777 /app
ENV SIIBRA_CACHEDIR=/app/cache

RUN chown -R nobody /app
USER nobody

# Expose port
EXPOSE 5000

# Start application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "5000"]
