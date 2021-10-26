import unittest
import os
import json
from urllib.parse import quote, quote_plus

from .util import Session

MULTILEVEL_HUMAN_ATLAS_ID='juelich/iav/atlas/v1.0.0/1'
ICBM_152_SPACE_ID = 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
JULICH_BRAIN_V29_PARC_ID='minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290'
INVALID_PARCELLATION_ID = 'INVALID_PARCELLATION_ID'
base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

class TestParcellation(unittest.TestCase):
    def test_all_parcellations(self):
        response = client.get('/v1_0/atlases/{}/parcellations'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID)))
        result_content = json.loads(response.content)
        assert response.status_code == 200
        assert len(result_content) > 0
        
    def test_get_one_parcellation_by_id(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            quote_plus(JULICH_BRAIN_V29_PARC_ID)))
        assert response.status_code == 200
        result_content = json.loads(response.content)
        assert result_content['id'] == {
            'kg': {
                'kgSchema': 'minds/core/parcellationatlas/v1.0.0',
                'kgId': '94c1125b-b87e-45e4-901c-00daee7f2579-290'
            }
        }
        assert result_content['name'] == 'Julich-Brain Cytoarchitectonic Maps 2.9'
        assert result_content['version']['name'] == '2.9'
    
    def test_all_regions_for_parcellations(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions?space_id={}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            quote_plus(JULICH_BRAIN_V29_PARC_ID),
            ICBM_152_SPACE_ID))

        assert response.status_code == 200
        result_content = json.loads(response.content)
        assert result_content[0]['children'] is not None

    def test_all_regions_for_parcellations_with_bad_request(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            quote_plus(INVALID_PARCELLATION_ID)))
        assert response.status_code == 400
        result_content = json.loads(response.content)
        assert result_content['detail'] == f'parcellation_id: {INVALID_PARCELLATION_ID} is not known'
