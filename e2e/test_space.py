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

class TestSpace(unittest.TestCase):
    def test_get_all_spaces(self):

        response = client.get('/v1_0/atlases/{}/spaces'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID)))
        result_content = json.loads(response.content)
        assert response.status_code == 200
        assert len(result_content) == 4

    def test_get_one_space(self):
        response = client.get('/v1_0/atlases/{}/spaces/{}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            quote_plus(ICBM_152_SPACE_ID)))
        
        result_content = json.loads(response.content)
        assert response.status_code == 200
        assert result_content['id'] == 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
        assert result_content['name'] == 'MNI152 2009c nonl asym'
        # TODO: Strange error. KeyError: 'name' when calling parcellation.supports_space
        # no error on second call
        assert len(result_content['availableParcellations']) > 0


    def test_get_invalid_space(self):
        response = client.get('/v1_0/atlases/{}/spaces/{}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            INVALID_SPACE_ID))
        result_content = json.loads(response.content)
        assert response.status_code == 400
        assert result_content['detail'] == f'space_id: {INVALID_SPACE_ID} is not known'

