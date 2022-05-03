# Copyright 2018-2022 Institute of Neuroscience and Medicine (INM-1),
# Forschungszentrum Jülich GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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


