from urllib.parse import quote, quote_plus
import os
from .util import Session
import pytest

MULTILEVEL_HUMAN_ATLAS_ID='juelich/iav/atlas/v1.0.0/1'
ICBM_152_SPACE_ID = 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
JULICH_BRAIN_V29_PARC_ID='minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290'
HOC1_LEFT_REGION_NAME = 'Area hOc1 (V1, 17, CalcS) left'

base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

regional_map_params = [
    (
        MULTILEVEL_HUMAN_ATLAS_ID,
        ICBM_152_SPACE_ID,
        JULICH_BRAIN_V29_PARC_ID,
        HOC1_LEFT_REGION_NAME,
        {
            'status_code': 200,
        }
    )
]

@pytest.mark.parametrize('atlas_id,space_id,parc_id,region_id,expected_response', regional_map_params)
def test_regional_map(atlas_id,space_id,parc_id,region_id,expected_response):

    response_info = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}/regional_map/info{}'.format(
        quote(atlas_id),
        quote_plus(parc_id),
        quote(region_id),
        f'?space_id={quote(space_id)}' if space_id else ''))
    
    assert expected_response.get('status_code') == response_info.status_code

    response_map = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}/regional_map/info{}'.format(
        quote(atlas_id),
        quote_plus(parc_id),
        quote(region_id),
        f'?space_id={quote(space_id)}' if space_id else ''))
    assert expected_response.get('status_code') == response_map.status_code
