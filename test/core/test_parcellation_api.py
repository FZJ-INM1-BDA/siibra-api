import json

from fastapi.testclient import TestClient

from app.app import app
import unittest
from urllib.parse import quote

client = TestClient(app)

ICBM_152_SPACE_ID='minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
ATLAS_ID = 'juelich/iav/atlas/v1.0.0/1'
PARCELLATION_ID = 'minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290'
INVALID_PARCELLATION_ID = 'INVALID_PARCELLATION_ID'
REGION_NAME = 'Ch 123 (Basal Forebrain) - left hemisphere'
REGION_ID = 'minds%2Fcore%2Fparcellationregion%2Fv1.0.0%2Fbb111a95-e04c-4987-8254-4af4ed8b0022'
REGION_BASAL = 'basal forebrain'
REGION_AREA_3B_RIGHT = 'Area 3b (PostCG) right'
HOC1_REGION_ID = 'minds%2Fcore%2Fparcellationregion%2Fv1.0.0%2F5151ab8f-d8cb-4e67-a449-afe2a41fb007'
INVALID_REGION_NAME = 'INVALID_REGION'
SPACE_ID = 'minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
VALID_MODALITY='EbrainsRegionalDataset'
VALID_MODALITY_INSTANCE_ID='https%3A%2F%2Fnexus.humanbrainproject.org%2Fv0%2Fdata%2Fminds%2Fcore%2Fdataset%2Fv1.0.0%2F87c6dea7-bdf7-4049-9975-6a9925df393f'

def test_get_all_parcellations():
    response = client.get(
        '/v1_0/atlases/{}/parcellations'.format(ATLAS_ID.replace('/', '%2F')),
    )
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert len(result_content) > 0


def test_get_one_parcellation_by_id():
    response = client.get('/v1_0/atlases/{}/parcellations/{}'.format(ATLAS_ID.replace('/', '%2F'), PARCELLATION_ID))
    url = response.url.split('atlases')[0]
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert result_content['id'] == {
        'kg': {
            'kgSchema': 'minds/core/parcellationatlas/v1.0.0',
            'kgId': '94c1125b-b87e-45e4-901c-00daee7f2579-290'
        }
    }
    assert result_content['name'] == 'Julich-Brain Cytoarchitectonic Maps 2.9'
    assert result_content['version']['name'] == '2.9'


def test_all_regions_for_parcellations():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions?space_id={}'.format(
        ATLAS_ID.replace('/', '%2F'),
        PARCELLATION_ID,
        ICBM_152_SPACE_ID))
    result_content = json.loads(response.content)
    assert response.status_code == 200
    # assert len(result_content) == 2
    assert result_content[0]['children'] is not None


def test_all_regions_for_parcellations_with_bad_request():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions'.format(ATLAS_ID.replace('/', '%2F'), INVALID_PARCELLATION_ID))
    assert response.status_code == 400
    result_content = json.loads(response.content)
    assert result_content['detail'] == f'parcellation_id: {INVALID_PARCELLATION_ID} is not known'


class TestSingleRegion(unittest.TestCase):

    def test_get_one_region_for_parcellation_without_extra_data(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}'.format(
            quote(ATLAS_ID),
            # nb must not be quote()
            PARCELLATION_ID,
            quote(REGION_BASAL)))
        result_content = json.loads(response.content)
        assert response.status_code == 200
        assert result_content['name'] == REGION_BASAL


    def test_get_one_region_for_parcellation_with_extra_data(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}?space_id={}'.format(ATLAS_ID.replace('/', '%2F'), PARCELLATION_ID, REGION_BASAL, SPACE_ID))
        result_content = json.loads(response.content)
        assert response.status_code == 200

        assert result_content['name'] == REGION_BASAL
        # Add Assertion for extra data


    def test_get_region_for_space_with_invalid_region_name(self):

        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}'.format(
            quote(ATLAS_ID),
            PARCELLATION_ID,
            quote(INVALID_REGION_NAME)))

        assert response.status_code == 404


    def test_get_region_with_correct_name(self):
        
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}'.format(
            quote(ATLAS_ID),
            PARCELLATION_ID,
            quote(REGION_AREA_3B_RIGHT)))
        assert response.status_code == 200
        
    # hasRegionalMap and other region map must be true
    def test_region_map(self):

        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}?space_id={}'.format(
            quote(ATLAS_ID),
            PARCELLATION_ID,
            quote(REGION_AREA_3B_RIGHT),
            quote(ICBM_152_SPACE_ID),
        ))
        jresp=json.loads(response.content)
        assert jresp.get('hasRegionalMap') is True

        info_url=jresp.get('links', {}).get('regional_map_info')
        map_url=jresp.get('links', {}).get('regional_map')
        assert info_url is not None
        assert map_url is not None

        # region map info
        
        if info_url is not None:
            response = client.get(info_url)
            assert response.status_code == 200
            info=json.loads(response.content)
            assert info.get('min') is not None
            assert info.get('max') is not None

        # region map
        if map_url is not None:
            response = client.get(map_url)
            assert response.status_code == 200



# TODO 500 response
# def test_regional_modality_by_id():
#     url = '/v1_0/atlases/{}/parcellations/{}/regions/{}/features/{}'.format(
#         ATLAS_ID.replace('/', '%2F'), PARCELLATION_ID, REGION_BASAL, VALID_MODALITY)
#     response = client.get(url)
#
#     # result_content = json.loads(response.content)
#     assert response.status_code == 200
