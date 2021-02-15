import json

from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)

ATLAS_ID = 'juelich/iav/atlas/v1.0.0/1'
SPACE_ID = 'minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
INVALID_SPACE_ID = 'INVALID_SPACE_ID'
REGION_NAME = 'Ch 123 (Basal Forebrain) - left hemisphere'
INVALID_REGION_NAME = 'INVALID_REGION'


def test_get_all_spaces():
    response = client.get('/atlases/{}/spaces'.format(ATLAS_ID.replace('/', '%2F')))
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert len(result_content) == 3


def test_get_one_space():
    response = client.get('/atlases/{}/spaces/{}'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID))
    url = response.url.split('atlases')[0]
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert result_content == {
        'id': 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2',
        'name': 'MNI 152 ICBM 2009c Nonlinear Asymmetric',
        'key': 'MNI_152_ICBM_2009C_NONLINEAR_ASYMMETRIC',
        'url': 'http://www.bic.mni.mcgill.ca/~vfonov/icbm/2009/mni_icbm152_nlin_asym_09c_nifti.zip',
        'ziptarget': 'mni_icbm152_t1_tal_nlin_asym_09c.nii',
        'links': {
            'regions': {
                'href': '{}atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2/regions'.format(url)
            },
            'templates': {
                'href': '{}atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2/templates'.format(url)
            },
            'parcellation_maps': {
                'href': '{}atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2/parcellation_maps'.format(url)
            }
        }
    }


def test_get_invalid_space():
    response = client.get('/atlases/{}/spaces/{}'.format(ATLAS_ID.replace('/', '%2F'), INVALID_SPACE_ID))
    result_content = json.loads(response.content)
    assert response.status_code == 404
    assert result_content['detail'] == 'space with id: {} not found'.format(INVALID_SPACE_ID)


def test_all_regions_for_space():
    response = client.get('/atlases/{}/spaces/{}/regions'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID))
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert len(result_content) == 2
    assert result_content[0]['children'] is not None


def test_get_region_for_space():
    response = client.get('/atlases/{}/spaces/{}/regions/{}'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID, REGION_NAME))
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
                -3.418699186991873,
                4.276422764227647,
                -8.605691056910572
            ],
            "volume_mm": 246,
            "surface_mm": 302.46898336714037,
            "is_cortical": False
        }
    }


def test_get_region_for_space_with_invalid_region_name():
    pass
    # response = client.get('/atlases/{}/spaces/{}/regions/{}'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID, INVALID_REGION_NAME))
    # result_content = json.loads(response.content)
    # assert response.status_code == 404
    # assert result_content['detail'] == 'region with name: {} not found'.format(INVALID_REGION_NAME)


def test_get_templates_for_space():
    response = client.get('/atlases/{}/spaces/{}/templates'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID))
    assert response.status_code == 200
    assert 'attachment' in response.headers['content-disposition']
    assert 'template-MNI_152_ICBM_2009c_Nonlinear_Asymmetric.nii' in response.headers['content-disposition']


def test_get_parcellation_maps_for_space():
    response = client.get('/atlases/{}/spaces/{}/parcellation_maps'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID))
    assert response.status_code == 200
    assert 'application/x-zip-compressed' in response.headers['content-type']
    assert 'attachment' in response.headers['content-disposition']
    assert 'maps-MNI_152_ICBM_2009c_Nonlinear_Asymmetric.zip' in response.headers['content-disposition']
