import unittest
from unittest.mock import MagicMock

from app import request_utils
import mock


class TestRequestUtils(unittest.TestCase):

    ATLAS_ID = 'juelich/iav/atlas/v1.0.0/1'
    REGION_NAME_VALID = 'Area 4p (PreCG)'
    REGION_NAME_INVALID = 'DUMMY_REGION'
    MODALITY_VALID = 'ReceptorDistribution'
    MODALITY_INVALID = 'DUMMY_MODALITY'
    BEARER_TOKEN = 'Bearer 1337'
    ARGS_TOKEN = '1337'
    PARCELLATION_NAME = 'Julich-Brain Cytoarchitectonic Maps 2.5'
    SPACE_NAME = 'MNI152 2009c nonl asym'
    request_mock = mock.MagicMock()
    request_mock.headers.return_value = {
        'Authorization': BEARER_TOKEN
    }

    def test_create_atlas(self):
        atlas = request_utils.create_atlas(self.ATLAS_ID)
        self.assertEqual(atlas.name, 'Multilevel Human Atlas')

    def test_query_data_with_wrong_modality(self):
        hits = request_utils.query_data(self.ATLAS_ID, self.MODALITY_INVALID, self.REGION_NAME_VALID)
        self.assertTrue(len(hits) == 0)

    def test_query_data_with_wrong_region(self):
        hits = request_utils.query_data(self.ATLAS_ID, self.MODALITY_VALID, self.REGION_NAME_INVALID)
        self.assertTrue(len(hits) == 0)

    def test_query_data_with_valid_values(self):

        hits = request_utils.query_data(self.ATLAS_ID, self.MODALITY_VALID, self.REGION_NAME_VALID)
        self.assertTrue(len(hits) != 0)
        self.assertIsNotNone(hits['data'])
        self.assertIsNotNone(hits['receptor_symbols'])

    def test_get_all_parcellations_for_space(self):
        parcellations = request_utils.get_parcellations_for_space(self.SPACE_NAME)
        self.assertGreater(len(parcellations), 0)

    def test_get_all_spaces_for_parcellation(self):
        spaces = request_utils.get_spaces_for_parcellation(self.PARCELLATION_NAME)
        self.assertGreater(len(spaces), 0)

    def test_base_url_without_redirect(self):
        self.request_mock.headers = {
            'host': 'localhost',
        }
        self.request_mock.url = 'http://localhost/v1_0/test'
        self.request_mock.base_url = 'http://localhost/'

        url = request_utils.get_base_url_from_request(self.request_mock)
        self.assertEqual(url, 'http://localhost/v1_0/')

    def test_base_url_with_redirect(self):
        self.request_mock.headers = {
            'host': 'localhost',
            'x-forwarded-proto': 'https'
        }
        self.request_mock.url = 'http://localhost/v1_0/test'
        self.request_mock.base_url = 'http://localhost/'

        url = request_utils.get_base_url_from_request(self.request_mock)
        self.assertEqual(url, 'https://localhost/v1_0/')


if __name__ == '__main__':
    unittest.main()

