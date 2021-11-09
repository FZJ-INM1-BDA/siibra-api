import os
import json
from urllib.parse import quote, quote_plus

import pytest
import unittest

from .util import Session
from .test_atlas import test_get_all_atlases

base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

atlases = test_get_all_atlases()

@pytest.mark.parametrize('atlas', atlases)
def test_all_parcellations(atlas):
    assert atlas.get('@id')
    response = client.get('/v1_0/atlases/{}/parcellations'.format(
        quote(atlas.get('@id'))))
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert len(result_content) > 0
    return result_content

atlas_parc = [(atlas, parc) for atlas in atlases for parc in test_all_parcellations(atlas)]

@pytest.mark.parametrize('atlas,parc', atlas_parc)
def test_parc(atlas,parc):
    assert atlas.get('@id')
    assert parc.get('@id')
    response = client.get('/v1_0/atlases/{}/parcellations/{}'.format(
        quote(atlas.get('@id')),
        quote_plus(parc.get('@id'))))
    assert response.status_code == 200
    

@pytest.mark.parametrize('atlas,parc', atlas_parc)
def test_parc_regions(atlas,parc):
    assert atlas.get('@id')
    assert parc.get('@id')
    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions'.format(
        quote_plus(atlas.get('@id')),
        quote_plus(parc.get('@id'))))
    assert response.status_code == 200
    regions = json.loads(response.content)
    assert type(regions) == list
    assert len(regions) > 0


# --- specific tests ---


MULTILEVEL_HUMAN_ATLAS_ID='juelich/iav/atlas/v1.0.0/1'
JULICH_BRAIN_V29_PARC_ID='minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290'

with open('e2e/expected/expected_julich29_detail.json') as fp:
    expected_julich_29 = json.load(fp)

def test_get_one_parcellation_by_id():
    response = client.get('/v1_0/atlases/{}/parcellations/{}'.format(
        quote(MULTILEVEL_HUMAN_ATLAS_ID),
        quote_plus(JULICH_BRAIN_V29_PARC_ID)))
    assert response.status_code == 200
    result_content = json.loads(response.content)
    case = unittest.TestCase()
    case.assertCountEqual(expected_julich_29, result_content)
