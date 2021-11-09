import os
import json
from urllib.parse import quote
import pytest
from .util import Session

base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

def test_get_all_atlases():
    response = client.get('/v1_0/atlases')
    assert response.status_code == 200
    result_content = json.loads(response.content)
    assert len(result_content) == 4
    return result_content


atlases = test_get_all_atlases()

@pytest.mark.parametrize('atlas', atlases)
def test_get_atlas_detail_works_on_all_atlases(atlas):
    assert atlas.get('@id')
    response = client.get('/v1_0/atlases/{}'.format(
        quote(atlas.get('@id'))))
    assert response.status_code == 200


# --- specific tests ---


MULTILEVEL_HUMAN_ATLAS_ID='juelich/iav/atlas/v1.0.0/1'
ICBM_152_SPACE_ID = 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
INVALID_SPACE_ID = 'INVALID_SPACE_ID'

def test_get_singe_atlas():
    response = client.get('/v1_0/atlases/{}'.format(
        quote(MULTILEVEL_HUMAN_ATLAS_ID)))
    assert response.status_code == 200
    result_content = json.loads(response.content)
    url = response.url.split('atlases')[0]
    assert result_content == {
        'id': MULTILEVEL_HUMAN_ATLAS_ID,
        '@type': 'juelich/iav/atlas/v1.0.0',
        'name': 'Multilevel Human Atlas',
        '@id': MULTILEVEL_HUMAN_ATLAS_ID
    }

def test_get_invalid_atlas():
    invalid_id = 'INVALID_ID'
    response = client.get('/v1_0/atlases/{}'.format(
        quote(invalid_id)))
    assert response.status_code == 404
    result_content = json.loads(response.content)
    assert result_content['detail'] == 'atlas with id: {} not found'.format(invalid_id)
