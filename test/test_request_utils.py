import unittest

from brainscapes.authentication import Authentication
from app import request_utils
from unittest.mock import Mock
import mock
from mock import patch


class TestRequestUtils(unittest.TestCase):

    mock = Mock()

    request = mock

    def test_create_atlas(self):
        atlas = request_utils.create_atlas()
        self.assertEqual(atlas.name, 'Multilevel Human Atlas')

    @patch.object(Authentication, 'set_token')
    def test_set_auth_token_bearer(self, auth_mock):
        request_mock = mock.MagicMock()
        request_mock.headers.return_value = {
            'Authorization': 'Bearer 1337'
        }
        with mock.patch('app.request_utils.request', request_mock):
            request_utils._set_auth_token()

        auth_mock.assert_called()

    @patch.object(Authentication, 'set_token')
    def test_set_auth_token_args(self, auth_mock):
        request_mock = mock.MagicMock()
        request_mock.args.return_value = {
            'token': '1337'
        }
        with mock.patch('app.request_utils.request', request_mock):
            request_utils._set_auth_token()

        auth_mock.assert_called()


if __name__ == '__main__':
    unittest.main()

