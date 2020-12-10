# Use python 3.8 as base image for the flask application
FROM python:3.8

# Upgrade pip to latest version
RUN python -m pip install --upgrade pip

# Install latest brainscapes client
RUN pip install brainscapes

# Copy the application and install dependencies
COPY ./app /app
WORKDIR /app

RUN python -m pip install -r requirements.txt
RUN python -m pip install connexion[swagger-ui]
RUN python -m pip install anytree
RUN python -m pip install pillow
RUN python -m pip install scikit-image

# Create directory for cache and set an environment variable for brainscapes
RUN mkdir cache
RUN chmod 777 cache
RUN chmod 777 /app
ENV BRAINSCAPES_CACHEDIR=/app/cache

# Expose flask port
EXPOSE 5000

# Start flask application
ENTRYPOINT ["python"]
CMD ["app.py"]
