from urllib.parse import quote, quote_plus
from .util import Session
import os
import pytest

base_url=os.getenv('SIIBRA_API_E2E_BASE_URL', 'http://localhost:5000')
client = Session(base_url=base_url)

FS_AVERAGE_SPACE_ID='minds/core/referencespace/v1.0.0/tmp-fsaverage'
MULTILEVEL_HUMAN_ATLAS_ID='juelich/iav/atlas/v1.0.0/1'
ICBM_152_SPACE_ID = 'minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2'
JULICH_BRAIN_V29_PARC_ID='minds/core/parcellationatlas/v1.0.0/94c1125b-b87e-45e4-901c-00daee7f2579-290'
HOC1_LEFT_REGION_NAME = 'Area hOc1 (V1, 17, CalcS) left'
SF_AMY_LEFT_REGION_NAME = 'SF (Amygdala) left '
INVALID_REGION_NAME = 'INVALID_REGION'

expected_hoc1_detail = {
  "@id": "minds/core/parcellationregion/v1.0.0/5151ab8f-d8cb-4e67-a449-afe2a41fb007",
  "@type": "minds/core/parcellationregion/v1.0.0",
  "name": "Area hOc1 (V1, 17, CalcS) left",
  "children": [],
  "rgb": [
    190,
    132,
    147
  ],
  'volumes': [{
    '@id': 'fzj/tmp/volume_type/v0.0.1/Area-hOc1-lh-colin',
    '@type': 'fzj/tmp/volume_type/v0.0.1',
    'detail': {},
    'id': 'fzj/tmp/volume_type/v0.0.1/Area-hOc1-lh-colin',
    'name': 'Probabilistic map of Area hOc1 (V1, 17, CalcS)',
    'type_id': 'fzj/tmp/volume_type/v0.0.1',
    'url': 'https://neuroglancer.humanbrainproject.eu/precomputed/data-repo-ng-bot/20210616-julichbrain-v2.9.0-complete-mpm/PMs/Area-hOc1/4.2/Area-hOc1_l_N10_nlin2Stdcolin27_4.2_publicP_026bcbe494dc4bfe702f2b1cc927a7c1.nii.gz',
    'volume_type': 'nii'
  },{
    '@id': 'fzj/tmp/volume_type/v0.0.1/Area-hOc1-lh-mni152',
    '@type': 'fzj/tmp/volume_type/v0.0.1',
    'detail': {},
    'id': 'fzj/tmp/volume_type/v0.0.1/Area-hOc1-lh-mni152',
    'name': 'Probabilistic map of Area hOc1 (V1, 17, CalcS)',
    'type_id': 'fzj/tmp/volume_type/v0.0.1',
    'url': 'https://neuroglancer.humanbrainproject.eu/precomputed/data-repo-ng-bot/20210616-julichbrain-v2.9.0-complete-mpm/PMs/Area-hOc1/4.2/Area-hOc1_l_N10_nlin2ICBM152asym2009c_4.2_publicP_026bcbe494dc4bfe702f2b1cc927a7c1.nii.gz',
    'volume_type': 'nii'
  }],
  "infos": [
    {
      "@id": "5c669b77-c981-424a-858d-fe9f527dbc07",
      "@type": "minds/core/dataset/v1.0.0",
      "id": "5c669b77-c981-424a-858d-fe9f527dbc07",
      "name": "Probabilistic cytoarchitectonic map of Area hOc1 (V1, 17, CalcS) (v2.4)",
      "description": "This dataset contains the distinct architectonic Area hOc1 (V1, 17, CalcS) in the individual, single subject template of the MNI Colin 27 as well as the MNI ICBM 152 2009c nonlinear asymmetric reference space. As part of the Julich-Brain cytoarchitectonic atlas, the area was identified using cytoarchitectonic analysis on cell-body-stained histological sections of 10 human postmortem brains obtained from the body donor program of the University of Düsseldorf. The results of the cytoarchitectonic analysis were then mapped to both reference spaces, where each voxel was assigned the probability to belong to Area hOc1 (V1, 17, CalcS). The probability map of Area hOc1 (V1, 17, CalcS) are provided in the NifTi format for each brain reference space and hemisphere. The Julich-Brain atlas relies on a modular, flexible and adaptive framework containing workflows to create the probabilistic brain maps for these structures. Note that methodological improvements and integration of new brain structures may lead to small deviations in earlier released datasets.\n\nOther available data versions of Area hOc1 (V1, 17, CalcS):\nAmunts et al. (2018) [Data set, v2.2] [DOI: 10.25493/8VRA-X28](https://doi.org/10.25493%2F8VRA-X28)\n\nThe most probable delineation of Area hOc1 (V1, 17, CalcS) derived from the calculation of a maximum probability map of all currently released Julich-Brain brain structures can be found here:\nAmunts et al. (2019) [Data set, v1.13] [DOI: 10.25493/Q3ZS-NV6](https://doi.org/10.25493%2FQ3ZS-NV6)\nAmunts et al. (2019) [Data set, v1.18] [DOI: 10.25493/8EGG-ZAR](https://doi.org/10.25493%2F8EGG-ZAR)\nAmunts et al. (2020) [Data set, v2.2] [DOI: 10.25493/TAKY-64D](https://doi.org/10.25493%2FTAKY-64D)",
      "urls": [
        {
          "cite": None,
          "doi": "10.25493/MXJ6-6DH"
        }
      ]
    }
  ],
  "label": 8,
  'centroids': None,
  'hasRegionalMap': None
}

hoc1_left_icbm = {
  "centroids": [
    {
      "@id": "69a85b6ac4bfa2c5a890eab3cb706020",
      "@type": "https://openminds.ebrains.eu/sands/CoordinatePoint",
      "coordinateSpace": {
        "@id": "minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2",
        "@type": "minds/core/referencespace/v1.0.0",
        "name": "MNI152 2009c nonl asym",
        "id": "minds/core/referencespace/v1.0.0/dafcffc5-4826-4bf1-8ff6-46b8a31ff8e2",
        "type_id": "minds/core/referencespace/v1.0.0",
        "volume_type": None,
        "volumes": None,
      },
      'coordinates': [
          {
              '@id': '63711742e03a64fe97435bc56d0c488c',
              '@type': 'https://openminds.ebrains.eu/core/dQuantitativeValue',
              'unit': {'@id': 'id.link/mm'},
              'value': -8.515510862347028
          },{
              '@id': '6ab0a050ff09225c680530b331afc9ce',
              '@type': 'https://openminds.ebrains.eu/core/dQuantitativeValue',
              'unit': {'@id': 'id.link/mm'},
              'value': -82.38838819846315
          },{
              '@id': '8d45976364d722ae316ad7c3a923dec6',
              '@type': 'https://openminds.ebrains.eu/core/dQuantitativeValue',
              'unit': {'@id': 'id.link/mm'},
              'value': 2.00540745659805
          }
      ],
    }
  ],
  'hasRegionalMap': True
}

parameters = [
    (
        MULTILEVEL_HUMAN_ATLAS_ID,
        None,
        JULICH_BRAIN_V29_PARC_ID,
        HOC1_LEFT_REGION_NAME,
        {
            'status_code': 200,
            'json': expected_hoc1_detail
        }
    ),
    (
        MULTILEVEL_HUMAN_ATLAS_ID,
        FS_AVERAGE_SPACE_ID,
        JULICH_BRAIN_V29_PARC_ID,
        HOC1_LEFT_REGION_NAME,
        {
            'status_code': 200,
            'json': expected_hoc1_detail
        }
    ),
    (
        MULTILEVEL_HUMAN_ATLAS_ID,
        ICBM_152_SPACE_ID,
        JULICH_BRAIN_V29_PARC_ID,
        HOC1_LEFT_REGION_NAME,
        {
            'status_code': 200,
            'json': {**expected_hoc1_detail, **hoc1_left_icbm}
        }
    ),
    (
        MULTILEVEL_HUMAN_ATLAS_ID,
        ICBM_152_SPACE_ID,
        JULICH_BRAIN_V29_PARC_ID,
        INVALID_REGION_NAME,
        {
            'status_code': 404
        }
    )
]

@pytest.mark.parametrize('atlas_id,space_id,parc_id,region_id,expected_response', parameters)
def test_single_known_region(atlas_id,space_id,parc_id,region_id,expected_response):

    response = client.get('/v1_0/atlases/{}/parcellations/{}/regions/{}{}'.format(
        quote(atlas_id),
        quote_plus(parc_id),
        quote(region_id),
        f'?space_id={quote(space_id)}' if space_id else ''))
    
    assert expected_response.get('status_code') == response.status_code
    if expected_response.get('status_code') == 200:
        import json
        # import unittest
        # case = unittest()
        assert expected_response.get('json') == json.loads(response.content)
