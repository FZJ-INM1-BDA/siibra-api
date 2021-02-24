import requests
import os
import base64
import json
import time

_client_id=os.getenv('EBRAINS_IAM_CLIENT_ID')
_client_secret=os.getenv('EBRAINS_IAM_CLIENT_SECRET')
_refresh_token=os.getenv('EBRAINS_IAM_REFRESH_TOKEN')

class InsufficientInfoException(Exception):
    pass

class TokenWrapper:
    def __init__(self, iam_url='https://services.humanbrainproject.eu/oidc', client_id=None, client_secret=None, refresh_token=None):
        
        self.iam_url=iam_url

        self.client_id=client_id
        self.client_secret=client_secret
        self.refresh_token=refresh_token
        self.access_token=None

    def _check_req(self):
        if self.client_id is None:
            raise InsufficientInfoException('client_id is required')
        if self.client_secret is None:
            raise InsufficientInfoException('client_secret is required')
        if self.refresh_token is None:
            raise InsufficientInfoException('refresh_token is required')
        return True

    # internal method, to get a new token
    def _get_new_token(self):
        self._check_req()
        url=f"{self.iam_url}/token"
        resp=requests.post(
            url,
            headers = {'content-type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            })
        json=resp.json()
        self.access_token=json['access_token']


    # decode urlsafe_b64 encoding of jwt
    # needs to add padding manually, as jwt spec allows missing padding, but python decode does not
    @staticmethod
    def decode(input):
        r=len(input)%4
        padding='='*(4-r)
        decoded=base64.urlsafe_b64decode(input+padding)
        return json.loads(decoded)

    # public method, to get valid token
    def get_token(self):

        # on init, get new token
        if self.access_token is None:
            self._get_new_token()

        # check token expiry. If less than 5 min get new token
        split=self.access_token.split('.')
        decoded=TokenWrapper.decode(split[1])
        expire_utc_sec=decoded['exp']
        current_utc_sec=time.time()
        if (expire_utc_sec - current_utc_sec) < (60 * 5):
            self._get_new_token()
            
        return self.access_token

token_wrapper=TokenWrapper(client_id=_client_id, client_secret=_client_secret, refresh_token=_refresh_token)

def get_public_token():
    return token_wrapper.get_token()

if __name__ == '__main__':
    print(get_public_token())