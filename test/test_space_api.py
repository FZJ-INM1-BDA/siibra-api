import json
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.app import app

from brainscapes.features import regionprops
from app.request_utils import _get_file_from_nibabel
from brainscapes import atlas

client = TestClient(app)

ATLAS_ID = 'juelich/iav/atlas/v1.0.0/1'
SPACE_ID = 'minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
INVALID_SPACE_ID = 'INVALID_SPACE_ID'


class MockRegionProps:
    def __init__(self, atlas, space):
        self.attrs = {'centroid_mm': [1,2,3], 'volume_mm': 4.0, 'surface_mm': 5.0, 'is_cortical': False}


regionprops.RegionProps = MockRegionProps

_get_file_from_nibabel = {}


def test_get_all_spaces():
    response = client.get('/v1_0/atlases/{}/spaces'.format(ATLAS_ID.replace('/', '%2F')))
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert len(result_content) == 3


def test_get_one_space():
    response = client.get('/v1_0/atlases/{}/spaces/{}'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID))
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
            'templates': {
                'href': '{}atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2/templates'.format(url)
            },
            'parcellation_maps': {
                'href': '{}atlases/juelich%2Fiav%2Fatlas%2Fv1.0.0%2F1/spaces/minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2/parcellation_maps'.format(url)
            }
        },
        'availableParcellations': [{'id': 'juelich/iav/atlas/v1.0.0/5',
                                    'name': 'Probabilistic Long White Matter Bundle '
                                            'Maps'},
                                   {'id': 'juelich/iav/atlas/v1.0.0/6',
                                    'name': 'Probabilistic Superficial Fibre Bundle '
                                            'Maps'},
                                   {'id': 'minds/core/parcellationatlas/v1.0.0/12fca5c5-b02c-46ce-ab9f-f12babf4c7e1',
                                    'name': 'Dictionary of functional modes (1024 '
                                            'dimensions)'},
                                   {'id': 'minds/core/parcellationatlas/v1.0.0/73f41e04-b7ee-4301-a828-4b298ad05ab8',
                                    'name': 'Dictionary of functional modes (128 '
                                            'dimensions)'},
                                   {'id': 'minds/core/parcellationatlas/v1.0.0/141d510f-0342-4f94-ace7-c97d5f160235',
                                    'name': 'Dictionary of functional modes (256 '
                                            'dimensions)'},
                                   {'id': 'minds/core/parcellationatlas/v1.0.0/63b5794f-79a4-4464-8dc1-b32e170f3d16',
                                    'name': 'Dictionary of functional modes (512 '
                                            'dimensions)'},
                                   {'id': 'minds/core/parcellationatlas/v1.0.0/d80fbab2-ce7f-4901-a3a2-3c8ef8a3b721',
                                    'name': 'Dictionary of functional modes (64 '
                                            'dimensions)'},
                                   {'id': 'minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579',
                                    'name': 'Julich-Brain Probabilistic '
                                            'Cytoarchitectonic Maps (v1.18)'},
                                   {'id': 'minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-25',
                                    'name': 'Julich-Brain Probabilistic '
                                            'Cytoarchitectonic Maps (v2.5)'}]
    }


def test_get_invalid_space():
    response = client.get('/v1_0/atlases/{}/spaces/{}'.format(ATLAS_ID.replace('/', '%2F'), INVALID_SPACE_ID))
    result_content = json.loads(response.content)
    assert response.status_code == 404
    assert result_content['detail'] == 'space with id: {} not found'.format(INVALID_SPACE_ID)


def test_get_templates_for_space():
    pass
    # Need to mock downlaoding file
    # response = client.get('/atlases/{}/spaces/{}/templates'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID))
    # assert response.status_code == 200
    # assert 'attachment' in response.headers['content-disposition']
    # assert 'template-MNI_152_ICBM_2009c_Nonlinear_Asymmetric.nii' in response.headers['content-disposition']


def test_get_parcellation_maps_for_space():
    response = client.get('/v1_0/atlases/{}/spaces/{}/parcellation_maps'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID))
    assert response.status_code == 200
    assert 'application/x-zip-compressed' in response.headers['content-type']
    assert 'attachment' in response.headers['content-disposition']
    assert 'maps-MNI_152_ICBM_2009c_Nonlinear_Asymmetric.zip' in response.headers['content-disposition']
