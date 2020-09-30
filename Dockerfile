# Use python 3 as base image for the flask application
FROM python:3

# Upgrade pip to latest version
RUN python -m pip install --upgrade pip

# Install latest brainscapes client
RUN pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple brainscapes

# Copy the application and install dependencies
COPY ./app /app
WORKDIR /app
RUN python -m pip install -r requirements.txt
RUN python -m pip install connexion[swagger-ui]
RUN python -m pip install anytree
RUN python -m pip install pillow
RUN python -m pip install scikit-image

# Expose flask port
EXPOSE 5000

# Start flask application
ENTRYPOINT ["python"]
CMD ["app.py"]
