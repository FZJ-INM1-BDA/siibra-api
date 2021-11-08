import unittest
import os
import json
from urllib.parse import quote, quote_plus

from .util import Session

MULTILEVEL_HUMAN_ATLAS_ID='juelich/iav/atlas/v1.0.0/1'
ICBM_152_SPACE_ID = 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
INVALID_SPACE_ID = 'INVALID_SPACE_ID'

base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

class TestAtlas(unittest.TestCase):

    def test_get_all_atlases(self):
        response = client.get('/v1_0/atlases')
        assert response.status_code == 200
        result_content = json.loads(response.content)
        assert len(result_content) == 4


    def test_get_singe_atlas(self):
        response = client.get('/v1_0/atlases/{}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID)))
        assert response.status_code == 200
        result_content = json.loads(response.content)
        url = response.url.split('atlases')[0]
        assert result_content == {
            'id': MULTILEVEL_HUMAN_ATLAS_ID,
            'name': 'Multilevel Human Atlas',
            'links': {
                'parcellations': {
                    'href': '{}atlases/{}/parcellations'.format(
                        url,
                        quote_plus(MULTILEVEL_HUMAN_ATLAS_ID)
                    )
                },
                'spaces': {
                    'href': '{}atlases/{}/spaces'.format(
                        url,
                        quote_plus(MULTILEVEL_HUMAN_ATLAS_ID)
                    )
                }
            }
        }


    def test_get_invalid_atlas(self):
        invalid_id = 'INVALID_ID'
        response = client.get('/v1_0/atlases/{}'.format(
            quote(invalid_id)))
        assert response.status_code == 404
        result_content = json.loads(response.content)
        assert result_content['detail'] == 'atlas with id: {} not found'.format(invalid_id)
