import unittest
import os
import json
from urllib.parse import quote, quote_plus
import pytest

from .util import Session

MULTILEVEL_HUMAN_ATLAS_ID='juelich/iav/atlas/v1.0.0/1'
ICBM_152_SPACE_ID = 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
BIGBRAIN_SPACE_ID = "minds/core/referencespace/v1.0.0/a1655b99-82f1-420f-a3c2-fe80fd4c8588"
COLIN_27_SPACE_ID = "minds/core/referencespace/v1.0.0/7f39f7be-445b-47c0-9791-e971c0b6d992"
INVALID_SPACE_ID = 'INVALID_SPACE_ID'

base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

test_space_param = [
    (quote(MULTILEVEL_HUMAN_ATLAS_ID), quote_plus(ICBM_152_SPACE_ID), "MNI152 2009c nonl asym", 13),
    (quote(MULTILEVEL_HUMAN_ATLAS_ID), quote_plus(BIGBRAIN_SPACE_ID), "Big Brain", 4),
    (quote(MULTILEVEL_HUMAN_ATLAS_ID), quote_plus(COLIN_27_SPACE_ID), "MNI Colin 27", 4),
]

@pytest.mark.parametrize("atlas_id,space_id,ex_space_name,ex_avail_parc_len", test_space_param)
def test_get_space(atlas_id,space_id,ex_space_name,ex_avail_parc_len):
    
    response = client.get('/v1_0/atlases/{}/spaces/{}'.format(
        atlas_id,
        space_id
    ))
    result_content = json.loads(response.content)
    assert result_content['name'] == ex_space_name

    # TODO: Strange error. KeyError: 'name' when calling parcellation.supports_space
    # no error on second call
    assert len(result_content['availableParcellations']) == ex_avail_parc_len

class TestSpace(unittest.TestCase):
    def test_get_all_spaces(self):

        response = client.get('/v1_0/atlases/{}/spaces'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID)))
        result_content = json.loads(response.content)
        assert response.status_code == 200
        assert len(result_content) == 4

    def test_get_invalid_space(self):
        response = client.get('/v1_0/atlases/{}/spaces/{}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            INVALID_SPACE_ID))
        result_content = json.loads(response.content)
        assert response.status_code == 400
        assert result_content['detail'] == f'space_id: {INVALID_SPACE_ID} is not known'

