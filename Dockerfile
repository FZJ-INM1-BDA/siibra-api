# Use python 3 as base image for the flask application
FROM python:3

#RUN useradd -p $(openssl passwd -1 password) myuser
#RUN usermod -aG sudo myuser

# Upgrade pip to latest version
RUN python -m pip install --upgrade pip

# Install latest brainscapes client
RUN git clone -b development https://jugit.fz-juelich.de/v.marcenko/brainscapes.git
RUN pip install -e brainscapes/.
#RUN pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple brainscapes

# Copy the application and install dependencies
#USER myuser
COPY ./app /app
WORKDIR /app

#USER root
RUN python -m pip install -r requirements.txt
RUN python -m pip install connexion[swagger-ui]
RUN python -m pip install anytree
RUN python -m pip install pillow
RUN python -m pip install scikit-image

#USER myuser

# Create directory for cache and set an environment variable for brainscapes
RUN mkdir cache
ENV BRAINSCAPES_CACHEDIR=/app/cache

# Expose flask port
EXPOSE 5000

# Start flask application
ENTRYPOINT ["python"]
CMD ["app.py"]
