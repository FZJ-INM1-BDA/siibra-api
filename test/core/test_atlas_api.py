import json

from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)

ATLAS_ID = 'juelich/iav/atlas/v1.0.0/1'


def test_get_all_atlases():
    response = client.get('/v1_0/atlases')
    assert response.status_code == 200
    result_content = json.loads(response.content)
    assert len(result_content) == 3


def test_get_singe_atlas():
    response = client.get('/v1_0/atlases/{}'.format(ATLAS_ID.replace('/', '%2F')))
    assert response.status_code == 200
    result_content = json.loads(response.content)
    url = response.url.split('atlases')[0]
    assert result_content == {
        'id': ATLAS_ID,
        'name': 'Multilevel Human Atlas',
        'links': {
            'parcellations': {
                'href': '{}atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/parcellations'.format(url)
            },
            'spaces': {
                'href': '{}atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces'.format(url)
            }
        }
    }


def test_get_invalid_atlas():
    invalid_id = 'INVALID_ID'
    response = client.get('/v1_0/atlases/{}'.format(invalid_id.replace('/', '%2F')))
    assert response.status_code == 404
    result_content = json.loads(response.content)
    assert result_content['detail'] == 'atlas with id: {} not found'.format(invalid_id)
