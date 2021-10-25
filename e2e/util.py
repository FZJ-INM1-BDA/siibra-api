import requests

class Session:
    def __init__(self, base_url):
        if base_url is None:
            raise ValueError(f'Session must initialise with base_url!')
        self.base_url = base_url
    
    def get(self, path: str, ignore_base_url=False):
        
        url = path if ignore_base_url else f'{self.base_url}{path}'
        resp = requests.get(url)
        if (resp.status_code >= 400):
            print(url)
        return resp