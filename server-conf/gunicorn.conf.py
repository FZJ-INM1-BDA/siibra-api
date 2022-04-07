
# gunicorn logging using uvicorn service working is a bit wonky
# one cannot customise the the format via gunicorn
# disable accesslog, and rely on middleware to log access, response & process time etc

# accesslog="-"
timeout=120
worker_class="uvicorn.workers.UvicornWorker"
workers=4
bind='127.0.0.1:5000'
wsgi_app="app.app:app"
