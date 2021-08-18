from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import os

_client_id = os.getenv('OAUTH_CLIENT_ID')
_client_secret = os.getenv('OAUTH_CLIENT_SECRET')
_refresh_token = ''


# Get OAuth2 token with client id and secret
# Consider to add url param to be able to get tokens for different resources (not only KG)
# Store tokens? Use refresh token? -> must create session or kind of user specific storage

def get_token():
    client = BackendApplicationClient(client_id=_client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(
        token_url='https://provider.com/oauth2/token',
        client_id=_client_id,
        client_secret=_client_secret
    )
    return token
#   auth = HTTPBasicAuth(client_id, client_secret)
#   client = BackendApplicationClient(client_id=client_id)
#   oauth = OAuth2Session(client=client)
#   token = oauth.fetch_token(token_url='https://provider.com/oauth2/token', auth=auth)


