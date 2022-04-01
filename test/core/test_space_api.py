import json
from urllib.parse import quote
from fastapi.testclient import TestClient
from siibra.features.ieeg import IEEGSessionModel

from app.app import app

client = TestClient(app)

ATLAS_ID = 'juelich/iav/atlas/v1.0.0/1'
SPACE_ID = 'minds%2Fcore%2Freferencespace%2Fv1.0.0%2Fdafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
INVALID_SPACE_ID = 'INVALID_SPACE_ID'


# class MockRegionProps:
#     def __init__(self, region, space):
#         self.attrs = {'centroid_mm': [1,2,3], 'volume_mm': 4.0, 'surface_mm': 5.0, 'is_cortical': False}
#
#
# region.RegionProps = MockRegionProps

get_file_from_nibabel = {}


def test_get_all_spaces():
    response = client.get('/v1_0/atlases/{}/spaces'.format(ATLAS_ID.replace('/', '%2F')))
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert len(result_content) == 4


def test_get_one_space():
    response = client.get('/v1_0/atlases/{}/spaces/{}'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID))
    url = response.url.split('atlases')[0]
    result_content = json.loads(response.content)
    assert response.status_code == 200
    assert result_content['@id'] == 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
    assert result_content['fullName'] == 'MNI152 2009c nonl asym'
    # TODO: Strange error. KeyError: 'name' when calling parcellation.supports_space
    # no error on second call
    # assert len(result_content['availableParcellations']) > 0


def test_get_invalid_space():
    response = client.get('/v1_0/atlases/{}/spaces/{}'.format(ATLAS_ID.replace('/', '%2F'), INVALID_SPACE_ID))
    result_content = json.loads(response.content)
    assert response.status_code == 400
    assert result_content['detail'] == f'space_id: {INVALID_SPACE_ID} is not known'

def test_ieeg_spatial_feature():
    url_tmpl='/v1_0/atlases/{}/spaces/{}/features{}?parcellation_id={}&region={}'

    # first get all spatial features given jba2.9 and hoc1 right
    url=url_tmpl.format(
        ATLAS_ID,
        "mni152",
        "",
        quote("2.9"),
        quote("hoc1 right")
    )
    response = client.get(url)
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json) > 0

    # now, for each, get detail, and verify inRoi attr
    for item in resp_json:
        if item.get("@type") != "siibra/features/ieegSession":
            continue
        detail_url=url_tmpl.format(
            ATLAS_ID,
            "mni152",
            '/' + quote(item.get("@id")),
            quote("2.9"),
            quote("hoc1 right")
        )
        resp = client.get(detail_url)
        assert resp.status_code == 200
        resp_json = resp.json()
        model = IEEGSessionModel(**resp_json)

        # session should be in roi
        assert model.in_roi == True

        # some electrode should be in roi
        assert any(
            electrode.in_roi
            for electrode in model.electrodes.values()
        )

        # electrodes in roi should have some ctpt in roi
        assert any(
            contact_pt.in_roi
            for electrode in model.electrodes.values()
            if electrode.in_roi
            for contact_pt in electrode.contact_points.values()
        )

        # the eletrodes not in roi should have all ctpt not in roi
        assert all(
            not contact_pt.in_roi
            for electrode in model.electrodes.values()
            if not electrode.in_roi
            for contact_pt in electrode.contact_points.values()
        )
    

def test_get_templates_for_space():
    pass
    # Need to mock downlaoding file
    # response = client.get('/atlases/{}/spaces/{}/templates'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID))
    # assert response.status_code == 200
    # assert 'attachment' in response.headers['content-disposition']
    # assert 'template-MNI_152_ICBM_2009c_Nonlinear_Asymmetric.nii' in response.headers['content-disposition']

# currently this test crashes the server
# for mni152
# def test_get_parcellation_maps_for_space():
#     response = client.get('/v1_0/atlases/{}/spaces/{}/parcellation_maps'.format(ATLAS_ID.replace('/', '%2F'), SPACE_ID))
#     assert response.status_code == 200
#     assert 'application/x-zip-compressed' in response.headers['content-type']
#     assert 'attachment' in response.headers['content-disposition']
