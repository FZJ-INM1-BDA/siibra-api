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

from siibra.atlas import REGISTRY
# from siibra.features import regionprops
import siibra as bs
import json
import nibabel as nib
from fastapi import HTTPException, Request
from .cache_redis import CacheRedis
import anytree

cache_redis = CacheRedis.get_instance()

def create_atlas(atlas_id=None):
    return REGISTRY.MULTILEVEL_HUMAN_ATLAS


def select_parcellation_by_id(atlas, parcellation_id):
    atlas.select_parcellation(find_parcellation_by_id(parcellation_id))


def query_data(modality, regionname, args=None):
    atlas = create_atlas()
    selected_region = atlas.find_regions(regionname)
    result = {}
    if modality in bs.features.modalities:
        if selected_region:
            atlas.select_region(selected_region[0])
            data = atlas.query_data(modality)
            if len(data) > 0:
                data[0]._load()
                result['data'] = data[0]
                result['receptor_symbols'] = bs.features.receptors.RECEPTOR_SYMBOLS
                return result
            else:
                raise HTTPException(
                    status_code=404,
                    detail='No data found for modality: {} in region: {}'.format(modality, regionname)
                )
    return []


def find_parcellation_by_id(atlas, parcellation_id):
    for parcellation in atlas.parcellations:
        if parcellation.id == parcellation_id:
            return parcellation
    return {}


def find_space_by_id(atlas, space_id):
    for space in atlas.spaces:
        if space.id.find(space_id) != -1:
            return space
    return {}


def create_region_json_object_tmp(region, space_id=None, atlas=None):
    region_json = {'name': region.name, 'children': []}
    if hasattr(region, 'rgb'):
        region_json['rgb'] = region.rgb
    if hasattr(region, 'fullId'):
        region_json['id'] = region.fullId
    if hasattr(region, 'labelIndex'):
        region_json['labelIndex'] = region.labelIndex
    region_json['availableIn'] = get_available_spaces_for_region(region)
    _add_children_to_region_tmp(region_json, region, space_id, atlas)
    return region_json


def _add_children_to_region_tmp(region_json, region, space_id=None, atlas=None):
    for child in region.children:
        o = create_region_json_object(child)
        # if space_id is not None and atlas is not None:
        #     get_region_props(space_id, atlas, o, child)
        if space_id is not None and atlas is not None:
            get_region_props_tmp(space_id, atlas, o, child)
        if child.children:
            _add_children_to_region_tmp(o, child, space_id, atlas)
        # else:
        #     if space_id is not None and atlas is not None:
        #         get_region_props_tmp(space_id, atlas, o, child)
                # get_region_props(space_id, atlas, o, child)
        region_json['children'].append(o)


def create_region_json_object(region, space_id=None, atlas=None):
    region_json = {'name': region.name, 'children': []}
    if hasattr(region, 'rgb'):
        region_json['rgb'] = region.rgb
    if hasattr(region, 'fullId'):
        region_json['id'] = region.fullId
    if hasattr(region, 'labelIndex'):
        region_json['labelIndex'] = region.labelIndex
    region_json['availableIn'] = get_available_spaces_for_region(region)
    # _add_children_to_region(region_json, region)
    return region_json


def _add_children_to_region(region_json, region):
    for child in region.children:
        o = create_region_json_object(child)

        if child.children:
            _add_children_to_region(o, child)
        region_json['children'].append(o)


def _get_file_from_nibabel(nibabel_object, nifti_type, space):
    filename = '{}-{}.nii'.format(nifti_type, space.name.replace(' ', '_'))
    # save nifti file in file-object
    nib.save(nibabel_object, filename)
    return filename


def split_id(kg_id: str):
    """
    Parameters:
        - kg_id

    Splitting the knowledge graph id into the schema and the id part.
    Only the id part is needed as a path parameter.
    """
    split_id = kg_id.split('/')
    return {
        'kg': {
            'kgSchema': '/'.join(split_id[0:-1]),
            'kgId': split_id[-1]
        }
    }


def _object_to_json(o):
    return {
        'id': o.id,
        'name': o.name
    }


def get_spaces_for_parcellation(parcellation: str):
    return [_object_to_json(bs.spaces[s]) for s in bs.parcellations[parcellation].maps.keys()]


def get_parcellations_for_space(space: str):
    result = []
    for p in bs.parcellations.items:
        for k in p.maps.keys():
            if bs.spaces[space].id in k.id:
                result.append(_object_to_json(p))
    return result


def get_base_url_from_request(request: Request):
    proto_header = 'x-forwarded-proto'
    proto = 'http'
    host = request.headers.get('host')
    api_version = str(request.url).replace(str(request.base_url), '').split('/')[0]
    if proto_header in request.headers:
        proto = request.headers.get(proto_header)

    return '{}://{}/{}/'.format(proto, host, api_version)


def get_available_spaces_for_region(region):
    result = []
    for s in bs.spaces:
        if region.parcellation.supports_space(s):
            result.append(_object_to_json(s))
    return result


# def get_region_props(space_id, atlas, region_json, region):
#     print('Getting regprops for: {}'.format(region))
#     atlas.select_region(region)
#     r_props = regionprops.RegionProps(atlas, find_space_by_id(atlas, space_id))
#     region_json['props'] = {}
#     region_json['props']['centroid_mm'] = list(r_props.attrs['centroid_mm'])
#     region_json['props']['volume_mm'] = r_props.attrs['volume_mm']
#     region_json['props']['surface_mm'] = r_props.attrs['surface_mm']
#     region_json['props']['is_cortical'] = r_props.attrs['is_cortical']


def get_region_props_tmp(space_id, atlas, region_json, region):
    print('Getting props for: {}'.format(str(region)))
    region_json['props'] = {}
    cache_value = cache_redis.get_value('{}_{}_{}_{}'.format(
        str(atlas.id),
        str(atlas.selected_parcellation.id),
        str(find_space_by_id(atlas, space_id).id),
        str(region)
    ))
    print(cache_value)
    if cache_value == 'invalid' or cache_value == 'None' or cache_value is None:
        region_json['props']['centroid_mm'] = ''
        region_json['props']['volume_mm'] = ''
        region_json['props']['surface_mm'] = ''
        region_json['props']['is_cortical'] = ''
    else:
        r_props = json.loads(cache_value)
        region_json['props']['centroid_mm'] = r_props['centroid_mm']
        region_json['props']['volume_mm'] = r_props['volume_mm']
        region_json['props']['surface_mm'] = r_props['surface_mm']
        region_json['props']['is_cortical'] = r_props['is_cortical']

def find_region_via_id(atlas,region_id):
    """
    Pure binder function to find regions via id by:
    - strict equality match (fullId.kgSchema + fullId.kgId)
    - atlas.find_regions fuzzy search first
    """

    def match_node(node):
        if node.attrs is None:
            return False
        if 'fullId' not in node.attrs:
            return False

        if node.attrs['fullId'] is None:
            return False
        full_id = node.attrs['fullId']
        if 'kg' not in full_id:
            return False
        full_id_kg=full_id['kg']
        return full_id_kg['kgSchema'] + '/' + full_id_kg['kgId'] == region_id

    fuzzy_regions=atlas.find_regions(region_id)

    region_tree=atlas.selected_parcellation.regiontree
    strict_equal_id=anytree.search.findall(region_tree, match_node)
    return [*strict_equal_id,*fuzzy_regions]
