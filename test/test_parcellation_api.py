import json

from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)

ATLAS_ID = 'juelich/iav/atlas/v1.0.0/1'
PARCELLATION_ID = 'minds%2Fcore%2Fparcellationatlas%2Fv1.0.0%2F94c1125b-b87e-45e4-901c-00daee7f2579-25'
INVALID_PARCELLATION_ID = 'INVALID_PARCELLATION_ID'


def test_get_all_parcellations():
    response = client.get(
        '/atlases/{}/parcellations'.format(ATLAS_ID.replace('/', '%2F')),
        headers={"Authorization": "Bearer token"}
    )
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert len(result_content) == 11


def test_get_one_parcellation_by_id():
    response = client.get('/atlases/{}/parcellations/{}'.format(ATLAS_ID.replace('/', '%2F'), PARCELLATION_ID))
    url = response.url.split('atlases')[0]
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert result_content == {
        'id': {
            'kg': {
                'kgSchema': 'minds/core/parcellationatlas/v1.0.0',
                'kgId': '94c1125b-b87e-45e4-901c-00daee7f2579-25'
            }
        },
        'name': 'Julich-Brain Probabilistic Cytoarchitectonic Maps (v2.5)',
        'version': '2.5'
    }
