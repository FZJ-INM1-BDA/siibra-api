# Copyright 2018-2020 Institute of Neuroscience and Medicine (INM-1), Forschungszentrum Jülich GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import os
import base64
import json
import time
from fastapi import HTTPException
from . import logger
from .siibra_custom_exception import SiibraCustomException

_client_id = os.getenv('EBRAINS_IAM_CLIENT_ID')
_client_secret = os.getenv('EBRAINS_IAM_CLIENT_SECRET')
_refresh_token = os.getenv('EBRAINS_IAM_REFRESH_TOKEN')


class InsufficientInfoException(Exception):
    pass


class TokenWrapper:
    def __init__(self, iam_url='https://services.humanbrainproject.eu/oidc', client_id=None, client_secret=None, refresh_token=None):
        
        self.iam_url = iam_url

        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None

    def _check_req(self):
        if self.client_id is None:
            raise InsufficientInfoException('client_id is required')
        if self.client_secret is None:
            raise InsufficientInfoException('client_secret is required')
        if self.refresh_token is None:
            raise InsufficientInfoException('refresh_token is required')
        return True

    def _get_new_token(self):
        """ internal method, to get a new token """
        self._check_req()
        url = f'{self.iam_url}/token'
        resp = requests.post(
            url,
            headers={'content-type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            })
        if resp.status_code != 200 or 'json' not in resp.headers['Content-Type']:
            logger.info(f'Could not reach {self.iam_url} to get access token')
            raise SiibraCustomException(message='siibra-api service is temporary not available', status_code=503)
        json_token = resp.json()
        self.access_token = json_token['access_token']

    @staticmethod
    def decode(input):
        """
        decode urlsafe_b64 encoding of jwt
        needs to add padding manually, as jwt spec allows missing padding, but python decode does not
        """
        r = len(input) % 4
        padding = '='*(4-r)
        decoded = base64.urlsafe_b64decode(input+padding)
        return json.loads(decoded)

    def get_token(self):
        """
        Get a valid token.
        Request a new token on init and check if token is expired for further requests.
        :return: AccessToken
        """
        if self.access_token is None:
            self._get_new_token()

        split = self.access_token.split('.')
        decoded = TokenWrapper.decode(split[1])
        expire_utc_sec = decoded['exp']
        current_utc_sec = time.time()
        if (expire_utc_sec - current_utc_sec) < (60 * 5):
            self._get_new_token()
            
        return self.access_token


token_wrapper = TokenWrapper(client_id=_client_id, client_secret=_client_secret, refresh_token=_refresh_token)


def get_public_token():
    return token_wrapper.get_token()


if __name__ == '__main__':
    print(get_public_token())
