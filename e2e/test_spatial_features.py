import pytest
from urllib.parse import quote, quote_plus
import json
import os
from .util import Session

MULTILEVEL_HUMAN_ATLAS_ID='juelich/iav/atlas/v1.0.0/1'
ICBM_152_SPACE_ID = 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
BIG_BRAIN_ID = 'bigbrain'
JULICH_BRAIN_V29_PARC_ID='minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290'
HOC1_LEFT_REGION_NAME = 'Area hOc1 (V1, 17, CalcS) left'
HOC1_RIGHT_REGION_NAME='Area hOc1 (V1, 17, CalcS) right'
SF_AMY_LEFT_REGION_NAME = 'SF (Amygdala) left '

julich_29_icbm152 = (
    MULTILEVEL_HUMAN_ATLAS_ID,
    ICBM_152_SPACE_ID,
    JULICH_BRAIN_V29_PARC_ID,
)

with open('e2e/expected/expected_bigbrain_voi_list.json') as fp:
    bigbrain_voi_list = json.load(fp)
big_brain_voi = (
    MULTILEVEL_HUMAN_ATLAS_ID,
    BIG_BRAIN_ID,
    None,
    None,
    'VolumeOfInterest',
)

with open('e2e/expected/expected_spatial_features_hoc1_right_short.json') as fp:
    ieeg_short = json.load(fp)

params = [
    (julich_29_icbm152 + (HOC1_LEFT_REGION_NAME, 'IEEG_Session', None, { 'status': 200, 'json': [] })),
    (julich_29_icbm152 + (HOC1_RIGHT_REGION_NAME, 'IEEG_Session',None, { 'status': 200, 'json': ieeg_short })),
    (big_brain_voi + (None, { 'status': 200, 'json': bigbrain_voi_list }))
]

base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

@pytest.mark.parametrize('atlas_id,space_id,parc_id,region_id,mod_id,feature_id,expected_resp', params)
def test_spatial_features(atlas_id,space_id,parc_id,region_id,mod_id,feature_id,expected_resp):

    query_param = ''
    if parc_id:
        query_param += f'?parcellation_id={quote_plus(parc_id)}'
        if region_id:
            query_param += f'&region_id={quote_plus(region_id)}'

    response = client.get('/v1_0/atlases/{atlas_id}/spaces/{space_id}/features/{mod_id}{feature_id}{query_param}'.format(
        atlas_id=quote(atlas_id),
        space_id=quote(space_id),
        mod_id=quote(mod_id),
        feature_id=f'/{feature_id}' if feature_id is not None else '',
        query_param=query_param
    ))

    assert response.status_code == 200
    if response.status_code == 200:
        assert json.loads(response.content) == expected_resp.get('json')
