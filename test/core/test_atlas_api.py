import json
import unittest

from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)


class TestAtlasApi(unittest.TestCase):

    ATLAS_ID = 'juelich/iav/atlas/v1.0.0/1'

    def test_get_all_atlases(self):
        response = client.get('/v2_0/atlases')
        self.assertEuqal(response.status_code, 200)
        result_content = json.loads(response.content)
        self.assertEqual(len(result_content), 4)

    def test_get_singe_atlas(self):
        response = client.get('/v2_0/atlases/{}'.format(self.ATLAS_ID.replace('/', '%2F')))
        self.assertEuqal(response.status_code, 200)
        result_content = json.loads(response.content)
        self.assertEqual(result_content['@id'], self.ATLAS_ID)

    def test_get_invalid_atlas(self):
        invalid_id = 'INVALID_ID'
        response = client.get('/v2_0/atlases/{}'.format(invalid_id.replace('/', '%2F')))
        self.assertEuqal(response.status_code, 400)
        result_content = json.loads(response.content)
        self.assertEqual(result_content['detail'], 'atlas_id: {} is not known'.format(invalid_id))
