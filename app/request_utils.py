# Copyright 2018-2020 Institute of Neuroscience and Medicine (INM-1), Forschungszentrum Jülich GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from brainscapes.authentication import Authentication
from brainscapes.atlas import REGISTRY
import brainscapes as bs

from fastapi import Request

import nibabel as nib


def _set_auth_token():
    auth = Authentication.instance()
    bearer_token = Request.headers.get("Authorization")
    if bearer_token:
        auth.set_token(bearer_token.replace("Bearer ", ""))
    elif Request.args['token']:
        auth.set_token(Request.args['token'])


def create_atlas():
    return REGISTRY.MULTILEVEL_HUMAN_ATLAS


def query_data(modality, regionname, args=None):
    atlas = create_atlas()
    selected_region = atlas.regiontree.find(regionname)
    result = {}
    if selected_region:
        atlas.select_region(selected_region[0])
        data = atlas.query_data(modality)
        data[0]._load()
        result['data'] = data[0]
        result['receptor_symbols'] = bs.features.receptors.RECEPTOR_SYMBOLS
        return result
    return []


def find_space_by_id(atlas, space_id):
    for space in atlas.spaces:
        if space.id.find(space_id):
            return space
    return {}    


def _add_children_to_region(region_json, region):
    for child in region.children:
        o = {'name': child.name, 'children': []}
        if hasattr(child, 'rgb'):
            o['rgb'] = child.rgb
        if hasattr(child, 'fullId'):
            o['id'] = child.fullId
        if hasattr(child, 'labelIndex'):
            o['labelIndex'] = child.labelIndex
        if child.children:
            _add_children_to_region(o, child)
        region_json['children'].append(o)


def _get_file_from_nibabel(nibabel_object, nifti_type, space):
    filename = '{}-{}.nii'.format(nifti_type, space.name.replace(' ','_'))
    # save nifti file in file-object
    nib.save(nibabel_object, filename)
    return filename        
