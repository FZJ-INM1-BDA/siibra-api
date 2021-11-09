from urllib.parse import quote, quote_plus
from .util import Session
import os
import pytest
import json
import unittest


MULTILEVEL_HUMAN_ATLAS_ID='juelich/iav/atlas/v1.0.0/1'
ICBM_152_SPACE_ID = 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
JULICH_BRAIN_V29_PARC_ID='minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290'
HOC1_LEFT_REGION_NAME = 'Area hOc1 (V1, 17, CalcS) left'
SF_AMY_LEFT_REGION_NAME = 'SF (Amygdala) left '

base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

misc = [
    (
        MULTILEVEL_HUMAN_ATLAS_ID,
        None,
        JULICH_BRAIN_V29_PARC_ID,
        SF_AMY_LEFT_REGION_NAME,
        'ReceptorDistribution',
        None,
        {
            'status_code': 200,
            'json': []
        }
    )
]


hoc1_left_base = (
    MULTILEVEL_HUMAN_ATLAS_ID,
    None,
    JULICH_BRAIN_V29_PARC_ID,
    HOC1_LEFT_REGION_NAME,
)


with open('./e2e/expected/expected_ebrains_ds_hoc1_short.json') as fp:
    expected_ebrains_short = json.load(fp)
with open('./e2e/expected/expected_ebrains_ds_hoc1.json') as fp:
    expected_ebrains = json.load(fp)
ebrains_base = ( hoc1_left_base + ('EbrainsRegionalDataset',) )
ebrains_base_param = [
    (
        None,
        { 'status_code': 200, 'json': expected_ebrains_short  }
    ),
    (
        'https://nexus.humanbrainproject.org/v0/data/minds/core/dataset/v1.0.0/3c722c10-9b76-4e64-9d4d-99d8eeb91471',
        { 'status_code': 200, 'json': expected_ebrains }
    )
]
ebrains_features_param = [ ( ebrains_base + param ) for param in ebrains_base_param ]


with open('./e2e/expected/expected_receptor_hoc1_short.json') as fp:
    expected_receptor_short = json.load(fp)
with open('./e2e/expected/expected_receptor_hoc1.json') as fp:
    expected_receptor_detail = json.load(fp)
receptor_base = ( hoc1_left_base + ('ReceptorDistribution', ) )
receptor_base_param = [
    (
        None,
        { 'status_code': 200, 'json': expected_receptor_short }
    ),
    (
        'https://nexus.humanbrainproject.org/v0/data/minds/core/dataset/v1.0.0/e715e1f7-2079-45c4-a67f-f76b102acfce',
        { 'status_code': 200, 'json': expected_receptor_detail }
    )
]
regional_features_parameters = [ (receptor_base + param) for param in receptor_base_param ]


with open('./e2e/expected/expected_connprofile_ds_hoc1_short.json') as fp:
    connprofile_short = json.load(fp)
with open('./e2e/expected/expected_connprofile_ds_hoc1.json') as fp:
    connprofile_detail = json.load(fp)
connprofile_base = (hoc1_left_base + ('ConnectivityProfile',))
connprofile_param = [
    (
        None,
        { 'status_code': 200, 'json': connprofile_short }
    ),
    (
        '8e7767c80dc1119e5307d71074de6c54',
        { 'status_code': 200, 'json': connprofile_detail }
    )
]

conn_features_parameters = [(connprofile_base + param) for param in connprofile_param]

def test_check_unittest():
    with pytest.raises(AssertionError):
        case = unittest.TestCase()
        case.assertCountEqual([], [1])


@pytest.mark.parametrize('atlas_id,space_id,parc_id,region_id,modality_id,feature_id,expected_response',[
    *regional_features_parameters,
    *ebrains_features_param,
    *conn_features_parameters,
    *misc
])
def test_regional_features(atlas_id,space_id,parc_id,region_id,modality_id,feature_id,expected_response):

    url = '/v1_0/atlases/{}/parcellations/{}/regions/{}/features/{}{}{}'.format(
        quote(atlas_id),
        quote_plus(parc_id),
        quote(region_id),
        quote(modality_id),
        f'/{quote_plus(feature_id)}' if feature_id is not None else '',
        f'?space_id={quote(space_id)}' if space_id else '')
    response = client.get(url)

    assert response.status_code == expected_response.get('status_code')
    if response.status_code == 200:
        json_response = json.loads(response.content)
        
        case = unittest.TestCase()
        case.assertCountEqual(json_response, expected_response.get('json'))
