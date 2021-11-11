import requests
import os

ci_flag = os.environ.get('SIIBRA_CI')

class Session:
    def __init__(self, base_url):
        if base_url is None:
            raise ValueError(f'Session must initialise with base_url!')
        self.base_url = base_url

    def __new__(cls, **kwargs):
        if ci_flag:
            from fastapi.testclient import TestClient
            from app.app import app
            client = TestClient(app)
            return client
        return super(Session, cls).__new__(cls)
    
    def get(self, path: str, ignore_base_url=False):
        
        url = path if ignore_base_url else f'{self.base_url}{path}'
        resp = requests.get(url)
        if (resp.status_code >= 400):
            print(url)
        return resp
