import unittest

from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)
ATLAS_ID = 'juelich/iav/atlas/v1.0.0/1'
PARCELLATION_ID = 'minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290'
SPACE_ID = 'minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
REGION_NAME = 'Ch 123 (Basal Forebrain) - left hemisphere'
REGION_ID = 'minds%2Fcore%2Fparcellationregion%2Fv1.0.0%2Fbb111a95-e04c-4987-8254-4af4ed8b0022'
VALID_FEATURE_ID = 'siibra/features/receptor/0a1f16d4ecab4cf8d96c5631d545e926'
INVALID_FEATURE_ID = 'INVALID'


class TestAtlasApi(unittest.TestCase):
    def test_get_feature_by_id(self):
        response = client.get('/v2_0/features/{}/?atlas_id={}&parcellation_id={}&space_id={}&region_id={}'.format(
            VALID_FEATURE_ID.replace('/', '%2F'),
            ATLAS_ID.replace('/', '%2F'),
            PARCELLATION_ID.replace('/', '%2F'),
            SPACE_ID,
            REGION_ID
            ))
        self.assertEqual(response.status_code, 200)

    def test_feature_not_found(self):
        response = client.get('/v2_0/features/{}/?atlas_id={}&parcellation_id={}&space_id={}&region_id={}'.format(
            INVALID_FEATURE_ID,
            ATLAS_ID.replace('/', '%2F'),
            PARCELLATION_ID.replace('/', '%2F'),
            SPACE_ID,
            REGION_ID
        ))
        self.assertEqual(response.status_code, 404)
        # self.assertEqual(response.detail, f'Feature with id {INVALID_FEATURE_ID} could not be found')
