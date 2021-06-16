import unittest
from app import ebrains_token
from app.siibra_custom_exception import SiibraCustomException
import os

# nb env needs to be set for tests to pass
client_id=os.getenv('EBRAINS_IAM_CLIENT_ID')
client_secret=os.getenv('EBRAINS_IAM_CLIENT_SECRET')
refresh_token=os.getenv('EBRAINS_IAM_REFRESH_TOKEN')

class TestTokenWrapper(unittest.TestCase):
    def test_no_client_id_raises(self):
        print(client_id, client_secret, refresh_token)
        tw=ebrains_token.TokenWrapper()
        self.assertRaises(SiibraCustomException, tw.get_token)
        
    def test_no_client_secret_raises(self):
        tw=ebrains_token.TokenWrapper(client_id=client_id)
        self.assertRaises(SiibraCustomException, tw.get_token)

    def test_no_refresh_token_raises(self):
        tw=ebrains_token.TokenWrapper(client_id=client_id, client_secret=client_secret)
        self.assertRaises(SiibraCustomException, tw.get_token)

    def test_all_param_present(self):
        tw=ebrains_token.TokenWrapper(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
        token=tw.get_token()


if __name__ == '__main__':
    unittest.main()
