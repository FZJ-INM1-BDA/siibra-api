FROM python:3
COPY app/. /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install connexion[swagger-ui]

EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["app.py"]
