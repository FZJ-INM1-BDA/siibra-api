import unittest
from unittest.mock import MagicMock
from fastapi import HTTPException

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

    JULICH_BRAIN_29_ID = 'minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290'
    MNI152_SPACE_ID = 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
    FP1_RIGHT = 'Area Fp1 (FPole) right'
    IEEG_ELECTRODE_MODALITY = 'IEEG_Electrode'
    IEEG_DATASET_MODALITY = 'IEEG_Dataset'

    def test_create_atlas(self):
        atlas = request_utils.create_atlas(self.ATLAS_ID)
        self.assertEqual(atlas.name, 'Multilevel Human Atlas')

    def test_get_regional_feature_with_wrong_modality(self):
        with self.assertRaises(HTTPException):
            hits = request_utils.get_regional_feature(atlas_id=self.ATLAS_ID, parcellation_id=self.PARCELLATION_NAME, modality_id=self.MODALITY_INVALID, region_id=self.REGION_NAME_VALID)

    def test_get_regional_feature_with_wrong_region(self):

        with self.assertRaises(HTTPException):
            hits = request_utils.get_regional_feature(atlas_id=self.ATLAS_ID, parcellation_id=self.PARCELLATION_NAME, modality_id=self.MODALITY_VALID, region_id=self.REGION_NAME_INVALID)

    def test_get_regional_feature_with_valid_values(self):

        hits = request_utils.get_regional_feature(atlas_id=self.ATLAS_ID, parcellation_id=self.PARCELLATION_NAME, modality_id=self.MODALITY_VALID, region_id=self.REGION_NAME_VALID)
        self.assertTrue(len(hits) != 0)
        self.assertTrue(all([ hit['@id'] is not None for hit in hits]))

    def test_get_all_parcellations_for_space(self):
        parcellations = request_utils.get_parcellations_for_space(self.SPACE_NAME)
        self.assertGreater(len(parcellations), 0)

    def test_get_all_spaces_for_parcellation(self):
        spaces = request_utils.get_spaces_for_parcellation(self.PARCELLATION_NAME)
        self.assertGreater(len(spaces), 0)

    # disabled awaiting fix of ieeg_electrode_extractor and ieeg_contact_point extractor in siibra-python

    # def test_get_spatial_features_ieeg_electrode(self):
    #     features=request_utils.get_spatial_features(
    #         self.ATLAS_ID,
    #         self.MNI152_SPACE_ID,
    #         self.IEEG_ELECTRODE_MODALITY,
    #         parc_id=self.JULICH_BRAIN_29_ID,
    #         region_id=self.FP1_RIGHT)

    #     self.assertGreater(len(features), 0)

    def test_get_spatial_features_ieeg_dataset(self):
        features=request_utils.get_spatial_features(
            self.ATLAS_ID,
            self.MNI152_SPACE_ID,
            self.IEEG_DATASET_MODALITY,
            parc_id=self.JULICH_BRAIN_29_ID,
            region_id=self.FP1_RIGHT)

        self.assertGreater(len(features), 0)

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

    def test_get_path_to_regional_map(self):
        import siibra as sb
        
        atlas=sb.atlases['human']
        assert atlas is not None
        atlas.select_region('hoc1 left')
        space_of_interest=sb.spaces['152']
        assert space_of_interest is not None

        path_to_file=request_utils.get_path_to_regional_map('tmp_req_id', atlas.selected_region, space_of_interest)
        assert path_to_file is not None

        import nibabel as nib
        nii=nib.load(path_to_file)
        assert nii is not None

if __name__ == '__main__':
    unittest.main()

