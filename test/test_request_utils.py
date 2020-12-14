import unittest

from brainscapes.authentication import Authentication
from app import request_utils
import mock
from mock import patch


class TestRequestUtils(unittest.TestCase):

    REGION_NAME_VALID = 'Area 4p (PreCG)'
    REGION_NAME_INVALID = 'DUMMY_REGION'
    MODALITY_VALID = 'ReceptorDistribution'
    MODALITY_INVALID = 'DUMMY_MODALITY'
    BEARER_TOKEN = 'Bearer 1337'
    ARGS_TOKEN = '1337'
    request_mock = mock.MagicMock()
    request_mock.headers.return_value = {
        'Authorization': BEARER_TOKEN
    }

    def test_create_atlas(self):
        atlas = request_utils.create_atlas()
        self.assertEqual(atlas.name, 'Multilevel Human Atlas')

    @patch.object(Authentication, 'set_token')
    def test_set_auth_token_bearer(self, auth_mock):
        with mock.patch('app.request_utils.request', self.request_mock):
            request_utils._set_auth_token()
        auth_mock.assert_called()

    @patch.object(Authentication, 'set_token')
    def test_set_auth_token_args(self, auth_mock):
        request_mock = mock.MagicMock()
        request_mock.args.return_value = {
            'token': self.ARGS_TOKEN
        }
        with mock.patch('app.request_utils.request', request_mock):
            request_utils._set_auth_token()

        auth_mock.assert_called()

    def test_query_data_with_wrong_modality(self):
        with mock.patch('app.request_utils.request', self.request_mock):
            hits = request_utils.query_data(self.MODALITY_INVALID, self.REGION_NAME_VALID)
            self.assertTrue(len(hits) == 0)

    def test_query_data_with_wrong_region(self):
        with mock.patch('app.request_utils.request', self.request_mock):
            hits = request_utils.query_data(self.MODALITY_VALID, self.REGION_NAME_INVALID)
            self.assertTrue(len(hits) == 0)

    def test_query_data_with_valid_values(self):
        with mock.patch('app.request_utils.request', self.request_mock):
            hits = request_utils.query_data(self.MODALITY_VALID, self.REGION_NAME_VALID)
            self.assertTrue(len(hits) != 0)


if __name__ == '__main__':
    unittest.main()

