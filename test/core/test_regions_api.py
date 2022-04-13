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
PARCELLATION_ID = 'minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-290'
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
INVALID_FEATURE_ID = 'INVALID'
VALID_FEATURE_ID = 'siibra/features/receptor/33c1e49ddd06eed636eb35e747378f40'

def test_all_regions_for_parcellations():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions?space_id={}'.format(
        ATLAS_ID.replace('/', '%2F'),
        PARCELLATION_ID,
        ICBM_152_SPACE_ID))
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert len(result_content) > 0


def test_all_regions_for_parcellations_with_search_param():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions?space_id={}'.format(
        ATLAS_ID.replace('/', '%2F'),
        PARCELLATION_ID,
        ICBM_152_SPACE_ID))
    full_length = len(json.loads(response.content))
    assert response.status_code == 200
    assert full_length > 0

    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions?space_id={}&find={}'.format(
        ATLAS_ID.replace('/', '%2F'),
        PARCELLATION_ID,
        ICBM_152_SPACE_ID,
        'left'))
    filtered_length = len(json.loads(response.content))
    assert response.status_code == 200
    assert full_length > filtered_length


def test_all_regions_for_parcellations_with_empty_find_result():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions?space_id={}&find={}'.format(
        ATLAS_ID.replace('/', '%2F'),
        PARCELLATION_ID,
        ICBM_152_SPACE_ID,
        INVALID_REGION_NAME))
    length = len(json.loads(response.content))
    assert response.status_code == 200
    assert length == 0


def test_all_regions_for_parcellations_with_bad_request():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions'.format(ATLAS_ID.replace('/', '%2F'), INVALID_PARCELLATION_ID))
    assert response.status_code == 400
    result_content = json.loads(response.content)
    assert result_content['detail'] == f'parcellation_id: {INVALID_PARCELLATION_ID} is not known'


class TestParcRegions(unittest.TestCase):

    def test_regions_return_fine(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions?space_id={}'.format(
            quote(ATLAS_ID),
            PARCELLATION_ID,
            quote(FS_AVERAGE_SPACE_ID),
        ))
        assert response.status_code == 200

    def test_regions_in_fsaverage(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions?space_id={}'.format(
            quote(ATLAS_ID),
            PARCELLATION_ID,
            quote(FS_AVERAGE_SPACE_ID),
        ))

        result_content = json.loads(response.content)
        assert result_content[0]['hasAnnotation'] is not None


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
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}?space_id={}'.format(
            ATLAS_ID.replace('/', '%2F'),
            PARCELLATION_ID,
            HOC1_LEFT_REGION_NAME,
            SPACE_ID))
        result_content = json.loads(response.content)
        assert response.status_code == 200

        assert result_content['name'] == HOC1_LEFT_REGION_NAME
        assert result_content['hasAnnotation']['bestViewPoint']['coordinates'] is not None

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

    def test_region_map_info(self):

        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}/regional_map/info?space_id={}'.format(
            quote(ATLAS_ID),
            PARCELLATION_ID,
            quote(REGION_AREA_3B_RIGHT),
            quote(ICBM_152_SPACE_ID),
        ))

        assert response.status_code == 200

        info = json.loads(response.content)
        assert info.get('min') is not None
        assert info.get('max') is not None

    def test_region_map(self):

        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}/regional_map/map?space_id={}'.format(
            quote(ATLAS_ID),
            PARCELLATION_ID,
            quote(REGION_AREA_3B_RIGHT),
            quote(ICBM_152_SPACE_ID),
        ))

        assert response.status_code == 200


class TestSingleRegionFeatures(unittest.TestCase):

    def test_regional_modality_by_id(self):
        url = '/v1_0/atlases/{}/parcellations/{}/regions/{}/features/{}'.format(
            quote_plus(ATLAS_ID),
            PARCELLATION_ID,
            HOC1_LEFT_REGION_NAME,
            VALID_FEATURE_ID)
        response = client.get(url)

        # result_content = json.loads(response.content)
        assert response.status_code == 200

    def test_feature_id_not_found(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}/features/{}'.format(
            quote(ATLAS_ID),
            PARCELLATION_ID,
            quote(HOC1_LEFT_REGION_NAME),
            INVALID_FEATURE_ID))
        assert response.status_code == 404

    #TODO not yet implemented with pydantic
    # def test_rest_connectivity(self):
    #     conn_id='e428cb6b-0110-4205-94ac-533ca5de6bb5'
    #     url='/v1_0/atlases/{atlas_id}/parcellations/{parcellation_id}/regions/{region_spec}/features/ConnectivityProfile/{conn_id}'.format(
    #         atlas_id=quote_plus(ATLAS_ID),
    #         parcellation_id=PARCELLATION_ID,
    #         region_spec=quote_plus(HOC1_LEFT_REGION_NAME),
    #         conn_id=conn_id
    #     )
    #     response=client.get(url)
    #     assert response.status_code == 200
    #     response_json=json.loads(response.content)
    #     column_names=response_json.get('__column_names')
    #     assert column_names is not None
    #     assert type(column_names) == list
    #     assert len(column_names) > 0
