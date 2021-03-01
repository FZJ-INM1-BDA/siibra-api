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
    PARCELLATION_NAME = 'Julich-Brain Probabilistic Cytoarchitectonic Maps (v2.5)'
    SPACE_NAME = 'MNI 152 ICBM 2009c Nonlinear Asymmetric'
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
        with mock.patch('app.request_utils.REGISTRY') as reg:
            atlas = reg.MULTILEVEL_HUMAN_ATLAS
            data_mock = MagicMock()
            data_mock._load.return_value
            atlas.query_data.return_value = [data_mock]
            hits = request_utils.query_data(self.MODALITY_VALID, self.REGION_NAME_VALID)
            self.assertTrue(len(hits) != 0)
            self.assertIsNotNone(hits['data'])
            self.assertIsNotNone(hits['receptor_symbols'])

    def test_get_all_parcellations_for_space(self):
        parcellations = request_utils.get_parcellations_for_space(self.SPACE_NAME)
        self.assertEqual(len(parcellations), 9)

    def test_get_all_spaces_for_parcellation(self):
        spaces = request_utils.get_spaces_for_parcellation(self.PARCELLATION_NAME)
        self.assertEqual(len(spaces), 2)


if __name__ == '__main__':
    unittest.main()

