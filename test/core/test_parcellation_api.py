import json

from fastapi.testclient import TestClient

from app.app import app
import unittest
from urllib.parse import quote, quote_plus

from app import logger
import logging
logger.setLevel(logging.DEBUG)
from siibra import logger
logger.setLevel(logging.DEBUG)

client = TestClient(app)

ICBM_152_SPACE_ID='minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
ATLAS_ID = 'juelich/iav/atlas/v1.0.0/1'
PARCELLATION_ID = 'minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290'
INVALID_PARCELLATION_ID = 'INVALID_PARCELLATION_ID'
REGION_NAME = 'Ch 123 (Basal Forebrain) - left hemisphere'
REGION_ID = 'minds%2Fcore%2Fparcellationregion%2Fv1.0.0%2Fbb111a95-e04c-4987-8254-4af4ed8b0022'
REGION_BASAL = 'basal forebrain'
REGION_AREA_3B_RIGHT = 'Area 3b (PostCG) right'
HOC1_LEFT_REGION_NAME='Area hOc1 (V1, 17, CalcS) left'
HOC1_RIGHT_REGION_NAME='Area+hOc1+%28V1%2C+17%2C+CalcS%29+right'
SF_AMY_LEFT_NAME='SF (Amygdala) left '
HOC1_REGION_ID = 'minds%2Fcore%2Fparcellationregion%2Fv1.0.0%2F5151ab8f-d8cb-4e67-a449-afe2a41fb007'
INVALID_REGION_NAME = 'INVALID_REGION'
SPACE_ID = 'minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
FS_AVERAGE_SPACE_ID='minds/core/referencespace/v1.0.0/tmp-fsaverage'
VALID_MODALITY='StreamlineCounts'
INVALID_MODALITY='INVALID%20MOD'
VALID_MODALITY_INSTANCE_ID='https%3A%2F%2Fnexus.humanbrainproject.org%2Fv0%2Fdata%2Fminds%2Fcore%2Fdataset%2Fv1.0.0%2F87c6dea7-bdf7-4049-9975-6a9925df393f'

def test_get_all_parcellations():
    response = client.get(
        '/v1_0/atlases/{}/parcellations'.format(ATLAS_ID.replace('/', '%2F')),
    )
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert len(result_content) > 0


def test_get_one_parcellation_by_id():
    response = client.get('/v1_0/atlases/{}/parcellations/{}'.format(ATLAS_ID.replace('/', '%2F'), PARCELLATION_ID.replace('/', '%2F')))
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert result_content['@id'] == PARCELLATION_ID
    # assert result_content['name'] == 'Julich-Brain Cytoarchitectonic Maps 2.9'
    # assert result_content['version']['name'] == '2.9'


def test_get_invalid_parcellation():
    response = client.get('/v1_0/atlases/{}/parcellations/{}'.format(ATLAS_ID.replace('/', '%2F'), INVALID_PARCELLATION_ID.replace('/', '%2F')))
    assert response.status_code == 400


def test_get_all_features_for_one_parcellation():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/features'.format(
        ATLAS_ID.replace('/', '%2F'),
        PARCELLATION_ID.replace('/', '%2F'))
    )
    assert response.status_code == 200
    result_content = json.loads(response.content)
    assert result_content.get('items')
    assert len(result_content.get('items')) > 0


def test_get_filtered_features_for_one_parcellation():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/features?type={}'.format(
        ATLAS_ID.replace('/', '%2F'),
        PARCELLATION_ID.replace('/', '%2F'),
        'siibra/features/connectivity/streamlineCounts')
    )
    assert response.status_code == 200
    result_content = json.loads(response.content)
    assert result_content.get('items')
    assert len(result_content.get('items')) > 0


def test_get_all_features_for_one_parcellation_with_wrong_type_filter():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/features?type={}'.format(
        ATLAS_ID.replace('/', '%2F'),
        PARCELLATION_ID.replace('/', '%2F'),
        'FOO')
    )
    assert response.status_code == 200
    result_content = json.loads(response.content)
    assert result_content.get('items')
    assert len(result_content.get('items')) == 0


def test_invalid_feature_modality():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/features/{}'.format(
        ATLAS_ID.replace('/', '%2F'),
        PARCELLATION_ID.replace('/', '%2F'),
        INVALID_MODALITY)
    )
    assert response.status_code == 404, f"Expecting 404, got {response.status_code}. Response is: {str(response.content)}"
