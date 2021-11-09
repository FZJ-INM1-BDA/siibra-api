import os
import json
from urllib.parse import quote
import pytest

from .util import Session
from .test_atlas import test_get_all_atlases

base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

atlases = test_get_all_atlases()

@pytest.mark.parametrize('atlas', atlases)
def test_get_all_spaces_from_atlas(atlas):
    url = '/v1_0/atlases/{}/spaces'.format(
        quote(atlas.get('@id'))
    )
    response = client.get(url)
    assert response.status_code == 200
    response_json = json.loads(response.content)
    assert len(response_json) > 0
    return response_json
    
atlas_spaces = [(atlas, space) for atlas in atlases for space in test_get_all_spaces_from_atlas(atlas)]

@pytest.mark.parametrize('atlas,space', atlas_spaces)
def test_all_spaces(atlas, space):
    url = '/v1_0/atlases/{}/spaces/{}'.format(
        quote(atlas.get('@id')),
        quote(space.get('@id'))
    )
    response = client.get(url)
    assert response.status_code == 200
    response_json = json.loads(response.content)
    assert response_json.get('name')
    assert response_json.get('id')

    # availableParcellations no longer in template
    # but parcellations should have 'spaces' attribute
    # assert response_json.get('availableParcellations')

def test_invalid_space():

    MULTILEVEL_HUMAN_ATLAS_ID='juelich/iav/atlas/v1.0.0/1'
    ICBM_152_SPACE_ID = 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
    INVALID_SPACE_ID = 'INVALID_SPACE_ID'
    url = '/v1_0/atlases/{}/spaces/{}'.format(
        quote(MULTILEVEL_HUMAN_ATLAS_ID),
        quote(INVALID_SPACE_ID)
    )
    response = client.get(url)
    assert response.status_code == 404
