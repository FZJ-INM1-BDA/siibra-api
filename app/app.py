import os

from flask import (
    render_template
)
import connexion
from os import environ

print(environ)
if "BRAINSCAPES_CACHEDIR" in environ:
    print(environ['BRAINSCAPES_CACHEDIR'])
print('userid: {}'.format(os.getegid()))

# Create the application instance
app = connexion.App(__name__, specification_dir='../')

# Read the swagger.yml file to configure the endpoints
app.add_api('app/swagger.yml')


# Create a URL route in our application for "/"
@app.route('/')
def home():
    return render_template('index.html')


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



