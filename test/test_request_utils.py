import unittest

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
    request_mock = mock.MagicMock()
    request_mock.headers.return_value = {
        'Authorization': BEARER_TOKEN
    }

    def test_create_atlas(self):
        atlas = request_utils.create_atlas(self.ATLAS_ID)
        self.assertEqual(atlas.name, 'Multilevel Human Atlas')

    def test_query_data_with_wrong_modality(self):
        hits = request_utils.query_data(self.MODALITY_INVALID, self.REGION_NAME_VALID)
        self.assertTrue(len(hits) == 0)

    def test_query_data_with_wrong_region(self):
        hits = request_utils.query_data(self.MODALITY_VALID, self.REGION_NAME_INVALID)
        self.assertTrue(len(hits) == 0)

    def test_query_data_with_valid_values(self):
        with mock.patch('app.request_utils.REGISTRY'):
            hits = request_utils.query_data(self.MODALITY_VALID, self.REGION_NAME_VALID)
            self.assertTrue(len(hits) != 0)
            self.assertIsNotNone(hits['data'])
            self.assertIsNotNone(hits['receptor_symbols'])


if __name__ == '__main__':
    unittest.main()

