import unittest
from urllib.parse import quote, quote_plus
import json
from .util import Session
import os

MULTILEVEL_HUMAN_ATLAS_ID='juelich/iav/atlas/v1.0.0/1'

ICBM_152_SPACE_ID = 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'

JULICH_BRAIN_V29_PARC_ID='minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290'

BASAL_REGION_NAME = 'basal forebrain'
HOC1_LEFT_REGION_NAME = 'Area hOc1 (V1, 17, CalcS) left'
HOC1_RIGHT_REGION_NAME = 'Area hOc1 (V1, 17, CalcS) right'
SF_AMY_LEFT_REGION_NAME = 'SF (Amygdala) left '
INVALID_REGION_NAME = 'foobar pizza'

EBRAINS_REGIONAL_DATASET_MODALITY_NAME = 'EbrainsRegionalDataset'

base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

class TestSingleRegion(unittest.TestCase):

    def test_get_one_region_for_parcellation_without_extra_data(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            # nb must not be quote()
            quote_plus(JULICH_BRAIN_V29_PARC_ID),
            quote(BASAL_REGION_NAME)))
        result_content = json.loads(response.content)
        assert response.status_code == 200
        assert result_content['name'] == BASAL_REGION_NAME


    def test_get_one_region_for_parcellation_with_extra_data(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}?space_id={}'.format(
            MULTILEVEL_HUMAN_ATLAS_ID.replace('/', '%2F'),
            quote_plus(JULICH_BRAIN_V29_PARC_ID),
            quote_plus(HOC1_LEFT_REGION_NAME),
            quote_plus(ICBM_152_SPACE_ID)))
        result_content = json.loads(response.content)
        assert response.status_code == 200

        assert result_content['name'] == HOC1_LEFT_REGION_NAME

        # spatial props
        props_components = result_content.get('props', {}).get('components', [])
        assert type(props_components) == list
        assert len(props_components) > 0
        
        assert type(props_components[0].get('centroid')) == list
        assert len(props_components[0].get('centroid')) == 3
        assert all([type(v) == float for v in props_components[0].get('centroid')])
        assert type(props_components[0].get('volume')) == float

        # _dataset_specs
        _dataset_specs = result_content.get('_dataset_specs')
        assert _dataset_specs is not None
        assert type(_dataset_specs) == list
        assert len(_dataset_specs) > 0
        # Add Assertion for extra data


    def test_get_region_for_space_with_invalid_region_name(self):

        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            quote_plus(JULICH_BRAIN_V29_PARC_ID),
            quote(INVALID_REGION_NAME)))

        assert response.status_code == 404


    def test_get_region_with_correct_name(self):
        
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            quote_plus(JULICH_BRAIN_V29_PARC_ID),
            quote(HOC1_LEFT_REGION_NAME)))
        assert response.status_code == 200

    def test_get_region_detail(self):

        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}?space_id={}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            quote_plus(JULICH_BRAIN_V29_PARC_ID),
            quote(HOC1_LEFT_REGION_NAME),
            quote(ICBM_152_SPACE_ID)
        ))

        region_json=json.loads(response.content)
        assert region_json.get('_dataset_specs') is not None
        assert type(region_json.get('_dataset_specs')) == list
        info_datasets = [ds for ds in region_json.get('_dataset_specs') if ds.get('@type') == 'minds/core/dataset/v1.0.0']
        assert len(info_datasets) > 0
        assert all([ds.get('description') is not None and ds.get('name') is not None for ds in info_datasets])
    

#     # hasRegionalMap and other region map must be true
    def test_region_map(self):

        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}?space_id={}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            quote_plus(JULICH_BRAIN_V29_PARC_ID),
            quote(HOC1_LEFT_REGION_NAME),
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
            response = client.get(info_url, ignore_base_url=True)
            assert response.status_code == 200
            info=json.loads(response.content)
            assert info.get('min') is not None
            assert info.get('max') is not None

        # region map
        if map_url is not None:
            response = client.get(map_url, ignore_base_url=True)
            assert response.status_code == 200

class TestSingleRegionFeatures(unittest.TestCase):

    def test_regional_modality_by_id(self):
        url = '/v1_0/atlases/{}/parcellations/{}/regions/{}/features/{}'.format(
            quote_plus(MULTILEVEL_HUMAN_ATLAS_ID),
            quote_plus(JULICH_BRAIN_V29_PARC_ID),
            BASAL_REGION_NAME,
            EBRAINS_REGIONAL_DATASET_MODALITY_NAME)
        response = client.get(url)
    
        assert response.status_code == 200

    def test_noresult_receptor(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}/features/ReceptorDistribution'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            # nb must not be quote()
            quote_plus(JULICH_BRAIN_V29_PARC_ID),
            quote(SF_AMY_LEFT_REGION_NAME)))
        result_content = json.loads(response.content)
        assert response.status_code == 200
        assert len(result_content) == 0

    def test_result_receptor(self):
        response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}/features/ReceptorDistribution'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            quote_plus(JULICH_BRAIN_V29_PARC_ID),
            quote(HOC1_LEFT_REGION_NAME)))
        result_content = json.loads(response.content)
        assert response.status_code == 200
        assert len(result_content) > 0
    
    def test_result_receptor_detail(self):
        receptor_dataset_id=r'Density%20measurements%20of%20different%20receptors%20for%20Area%20hOc1%20(V1%2C%2017%2C%20CalcS)%20%5Bhuman%2C%20v1.0%5D'
        url='/v1_0/atlases/{}/parcellations/{}/regions/{}/features/ReceptorDistribution/{}'.format(
            quote(MULTILEVEL_HUMAN_ATLAS_ID),
            quote_plus(JULICH_BRAIN_V29_PARC_ID),
            quote(HOC1_LEFT_REGION_NAME),
            receptor_dataset_id)
        response = client.get(url)
        assert response.status_code == 200

    def test_result_ieeg(self):
        url='/v1_0/atlases/{atlas_id}/spaces/{space_id}/features/IEEG_Session?parcellation_id={parc_id}&region={region_id}'.format(
            atlas_id=quote_plus(MULTILEVEL_HUMAN_ATLAS_ID),
            space_id=quote_plus(ICBM_152_SPACE_ID),
            parc_id=quote_plus(JULICH_BRAIN_V29_PARC_ID),
            region_id=quote_plus(HOC1_RIGHT_REGION_NAME),
        )
        response=client.get(url)
        result_content = json.loads(response.content)
        assert response.status_code == 200
        assert len(result_content) > 0
        

    def test_no_result_ieeg(self):
        url='/v1_0/atlases/{atlas_id}/spaces/{space_id}/features/IEEG_Session?parcellation_id={parc_id}&region={region_id}'.format(
            atlas_id=quote_plus(MULTILEVEL_HUMAN_ATLAS_ID),
            space_id=quote_plus(ICBM_152_SPACE_ID),
            parc_id=quote_plus(JULICH_BRAIN_V29_PARC_ID),
            region_id=quote_plus(HOC1_LEFT_REGION_NAME),
        )
        response=client.get(url)
        result_content = json.loads(response.content)
        assert response.status_code == 200
        # hoc1 left should have no ieeg result
        assert len(result_content) == 0

    def test_rest_connectivity(self):
        conn_id='e428cb6b-0110-4205-94ac-533ca5de6bb5'
        url='/v1_0/atlases/{atlas_id}/parcellations/{parcellation_id}/regions/{region_spec}/features/ConnectivityProfile/{conn_id}'.format(
            atlas_id=quote_plus(MULTILEVEL_HUMAN_ATLAS_ID),
            parcellation_id=quote_plus(JULICH_BRAIN_V29_PARC_ID),
            region_spec=quote_plus(HOC1_LEFT_REGION_NAME),
            conn_id=conn_id
        )
        response=client.get(url)
        assert response.status_code == 200
        response_json=json.loads(response.content)
        column_names=response_json.get('__column_names')
        assert column_names is not None
        assert type(column_names) == list
        assert len(column_names) > 0
