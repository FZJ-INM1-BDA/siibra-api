import json

from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)

ATLAS_ID = 'juelich/iav/atlas/v1.0.0/1'
PARCELLATION_ID = 'minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-25'
INVALID_PARCELLATION_ID = 'INVALID_PARCELLATION_ID'
REGION_NAME = 'Ch 123 (Basal Forebrain) - left hemisphere'
INVALID_REGION_NAME = 'INVALID_REGION'
SPACE_ID = 'minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'


def test_get_all_parcellations():
    response = client.get(
        '/v1_0/atlases/{}/parcellations'.format(ATLAS_ID.replace('/', '%2F')),
        headers={"Authorization": "Bearer token"}
    )
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert len(result_content) == 12


def test_get_one_parcellation_by_id():
    response = client.get('/v1_0/atlases/{}/parcellations/{}'.format(ATLAS_ID.replace('/', '%2F'), PARCELLATION_ID))
    url = response.url.split('atlases')[0]
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert result_content['id'] == {
        'kg': {
            'kgSchema': 'minds/core/parcellationatlas/v1.0.0',
            'kgId': '94c1125b-b87e-45e4-901c-00daee7f2579-25'
        }
    }
    assert result_content['name'] == 'Julich-Brain Probabilistic Cytoarchitectonic Maps (v2.5)'
    assert result_content['version'] == '2.5'


def test_all_regions_for_parcellations():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions'.format(ATLAS_ID.replace('/', '%2F'), PARCELLATION_ID))
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert len(result_content) == 2
    assert result_content[0]['children'] is not None


def test_all_regions_for_parcellations_with_bad_request():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions'.format(ATLAS_ID.replace('/', '%2F'), INVALID_PARCELLATION_ID))
    assert response.status_code == 400
    result_content = json.loads(response.content)
    assert result_content['detail'] == 'The requested parcellation is not supported by the selected atlas.'


def test_get_one_region_for_parcellation_without_extra_data():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}'.format(ATLAS_ID.replace('/', '%2F'), PARCELLATION_ID, REGION_NAME))
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert result_content == {
        "name": "Ch 123 (Basal Forebrain) - left hemisphere",
        "children": [],
        "rgb": [
            200,
            200,
            200
        ],
        "id": {
            "kg": {
                "kgSchema": "minds/core/parcellationregion/v1.0.0",
                "kgId": "bb111a95-e04c-4987-8254-4af4ed8b0022"
            }
        },
        "labelIndex": 62,
        'links': {'features': 'http://testserver/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-25/regions/Ch '
                              '123 (Basal Forebrain) - left hemisphere/features'},
    }


def test_get_one_region_for_parcellation_with_extra_data():
    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}?space_id={}'.format(ATLAS_ID.replace('/', '%2F'), PARCELLATION_ID, REGION_NAME, SPACE_ID))
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert result_content == {
        "name": "Ch 123 (Basal Forebrain) - left hemisphere",
        "children": [],
        "rgb": [
            200,
            200,
            200
        ],
        "id": {
            "kg": {
                "kgSchema": "minds/core/parcellationregion/v1.0.0",
                "kgId": "bb111a95-e04c-4987-8254-4af4ed8b0022"
            }
        },
        "labelIndex": 62,
        "props": {
            "centroid_mm": [
                1,
                2,
                3
            ],
            "volume_mm": 4.0,
            "surface_mm": 5.0,
            "is_cortical": False
        },
        'links': {'features': 'http://testserver/v1_0/atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations/minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-25/regions/Ch '
                              '123 (Basal Forebrain) - left hemisphere/features'}
    }


def test_get_region_for_space_with_invalid_region_name():
    pass
    # response = client.get('/atlases/{}/spaces/{}/regions/{}'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID, INVALID_REGION_NAME))
    # result_content = json.loads(response.content)
    # assert response.status_code == 404
    # assert result_content['detail'] == 'region with name: {} not found'.format(INVALID_REGION_NAME)
