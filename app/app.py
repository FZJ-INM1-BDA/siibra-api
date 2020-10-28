from flask import (
    render_template,
    request
)
import connexion

import requests

import os

# Create the application instance
app = connexion.App(__name__, specification_dir='../')

# Read the swagger.yml file to configure the endpoints
app.add_api('app/swagger.yml')


# Create a URL route in our application for "/"
@app.route('/')
def home():
    return render_template('index.html')


@app.app.before_request
def before_request_func():
    test_url = request.url
    headers = request.headers.get
    test_list = ['.css', '.js', '.png', '.gif', '.json', '.ico']
    res = any(ele in test_url for ele in test_list)

    if 'BRAINSCAPES_ENVIRONMENT' in os.environ:
        if os.environ['BRAINSCAPES_ENVIRONMENT'] == 'PRODUCTION':
            print('******* Im on production ********')
            if not res:
                payload = {
                        'idsite': 13,
                        'rec': 1,
                        'action_name': 'brainscapes_api',
                        'url': request.url,
                        '_id': 'my_ip',
                        'lang':  request.headers.get('Accept-Language'),
                        'ua': request.headers.get('User-Agent')
                }
                try:
                    r = requests.get('https://stats.humanbrainproject.eu/matomo.php', params=payload)
                    print('Matomo logging with status: {}'.format(r.status_code))
                except:
                    print('Could not log to matomo instance')
        else:
            print('Request for: {}'.format(request.url))


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
