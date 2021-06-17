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

import siibra as bs
import json
import nibabel as nib
from fastapi import HTTPException, Request
from .cache_redis import CacheRedis
import anytree
from siibra.features import feature as feature_export, classes as feature_classes, connectivity as connectivity_export, \
    receptors as receptors_export, genes as genes_export, ebrainsquery as ebrainsquery_export
import hashlib
import os
from .diskcache import fanout_cache, CACHEDIR
from . import logger
from siibra.volumesrc import VolumeSrc, NiftiVolume, NgVolume
from siibra import commons as siibra_commons

cache_redis = CacheRedis.get_instance()


def create_atlas(atlas_id=None):
    if atlas_id is None:
        raise HttpException(status_code=400, detail='atlas_id is required!')
    if atlas_id not in bs.atlases:
        raise HttpException(status_code=404, detail=f'atlas_id {atlas_id} not found!')
    return bs.atlases[atlas_id]


def select_parcellation_by_id(atlas, parcellation_id):
    atlas.select_parcellation(find_parcellation_by_id(parcellation_id))


def find_parcellation_by_id(atlas, parcellation_id):
    for parcellation in atlas.parcellations:
        if parcellation.id == parcellation_id:
            return parcellation
    return {}


def find_space_by_id(atlas, space_id):
    try:
        found_space = bs.spaces[space_id]
        return found_space if found_space in atlas.spaces else None
    except IndexError:
        return None


def create_region_json_response(region, space_id=None, atlas=None):
    region_json = _create_region_json_object(region, space_id, atlas)
    _add_children_to_region(region_json, region, space_id, atlas)
    return region_json


def _add_children_to_region(region_json, region, space_id=None, atlas=None):
    for child in region.children:
        o = _create_region_json_object(child)
        if space_id is not None and atlas is not None:
            get_region_props_tmp(space_id, atlas, o, child)
        if child.children:
            _add_children_to_region(o, child, space_id, atlas)
        region_json['children'].append(o)


def _create_region_json_object(region, space_id=None, atlas=None):
    region_json = {'name': region.name, 'children': []}
    if hasattr(region, 'rgb'):
        region_json['rgb'] = region.rgb
    if hasattr(region, 'fullId'):
        region_json['id'] = region.fullId
    if hasattr(region, 'labelIndex'):
        region_json['labelIndex'] = region.labelIndex
    if hasattr(region, 'attrs'):
        region_json['volumeSrc'] = region.attrs.get('volumeSrc', {})
    region_json['availableIn'] = get_available_spaces_for_region(region)

    region_json['hasRegionalMap'] = region.has_regional_map(bs.spaces[space_id], bs.commons.MapType.CONTINUOUS) if space_id is not None else None

    return region_json


def _get_file_from_nibabel(nibabel_object, nifti_type, space):
    filename = '{}-{}.nii'.format(nifti_type, space.name.replace(' ', '_'))
    # save nifti file in file-object
    nib.save(nibabel_object, filename)
    return filename


def get_cached_file(filename: str, fn: callable):
    cached_full_path = os.path.join(CACHEDIR, filename)

    # if path does not exist, call the provided fn
    if not os.path.exists(cached_full_path):
        fn(cached_full_path)
    
    return cached_full_path


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
    return [_object_to_json(bs.spaces[s]) for s in bs.parcellations[parcellation].volume_src.keys()]


def get_parcellations_for_space(space):
    space_instance = bs.spaces[space] if type(space) is str else space
    return [_object_to_json(p) for p in bs.parcellations if p.supports_space(space_instance)]


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


def find_region_via_id(atlas, region_id):
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
        full_id_kg = full_id['kg']
        return full_id_kg['kgSchema'] + '/' + full_id_kg['kgId'] == region_id

    fuzzy_regions=atlas.find_regions(region_id)

    region_tree=atlas.selected_parcellation.regiontree
    strict_equal_id=anytree.search.findall(region_tree, match_node)
    return [*strict_equal_id,*fuzzy_regions]


# allow for fast fails
SUPPORTED_FEATURES = [genes_export.GeneExpression, connectivity_export.ConnectivityProfile, receptors_export.ReceptorDistribution, ebrainsquery_export.EbrainsRegionalDataset]


@fanout_cache.memoize(typed=True, expire=60*60)
def get_regional_feature(atlas_id, parcellation_id, region_id, modality_id, gene=None):
    # select atlas by id
    if modality_id not in feature_classes:
        # modality_id not found in feature_classes
        raise HTTPException(status_code=400, detail=f'{modality_id} is not a valid modality')

    # fail fast if not in supported feature list
    if feature_classes[modality_id] not in SUPPORTED_FEATURES:
        raise HTTPException(status_code=501, detail=f'feature {modality_id} has not yet been implmented')
    
    if not issubclass(feature_classes[modality_id], feature_export.RegionalFeature):
        # modality_id is not a global feature, return empty array
        return []

    # select atlas by id
    atlas = create_atlas(atlas_id)
    # select atlas parcellation
    try:
        # select atlas parcellation
        atlas.select_parcellation(parcellation_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail='The requested parcellation is not supported by the selected atlas.'
        )
    regions = find_region_via_id(atlas, region_id)

    if len(regions) == 0:
        raise HTTPException(status_code=404, detail=f'Region with id {region_id} not found!')
    
    atlas.select_region(regions[0])
    try:
        got_features = atlas.get_features(modality_id, gene=gene)
    except Exception:
        raise HTTPException(status_code=404, detail=f'Could not get features for region with id {region_id}')

    if feature_classes[modality_id] == ebrainsquery_export.EbrainsRegionalDataset:
        return [{
            '@id': kg_rf_f.id,
            'src_name': kg_rf_f.name,
            '__detail': kg_rf_f.detail
        } for kg_rf_f in got_features]
    if feature_classes[modality_id] == genes_export.GeneExpression:
        return [{
            '@id': hashlib.md5(str(gene_feat).encode("utf-8")).hexdigest(),
            '__donor_info':gene_feat.donor_info,
            '__gene':gene_feat.gene,
            '__probe_ids':gene_feat.probe_ids,
            '__mri_coord':gene_feat.mri_coord,
            '__z_scores':gene_feat.z_scores,
            '__expression_levels':gene_feat.expression_levels
        } for gene_feat in got_features]
    if feature_classes[modality_id] == connectivity_export.ConnectivityProfile:
        return [{
            "@id": conn_pr.src_name,
            "src_name": conn_pr.src_name,
            "src_info": conn_pr.src_info,
            "kgSchema":  conn_pr.kg_schema,
            "kgId":  conn_pr.kg_id,
            "__column_names": conn_pr.column_names,
            "__profile": conn_pr.profile,
        } for conn_pr in got_features ]
    if feature_classes[modality_id] == receptors_export.ReceptorDistribution:
        return [{
            "@id": receptor_pr.name,
            "name": receptor_pr.name,
            "info": receptor_pr.info,
            "__receptor_symbols": receptors_export.RECEPTOR_SYMBOLS,
            "__files": receptor_pr.files,
            "__data": {
                "__profiles": receptor_pr.profiles,
                "__autoradiographs": receptor_pr.autoradiographs,
                "__fingerprint": receptor_pr.fingerprint,
                "__profile_unit": receptor_pr.profile_unit,
            },
        } for receptor_pr in got_features ]
    raise HTTPException(status_code=501, detail=f'feature {modality_id} has not yet been implmented')


@fanout_cache.memoize(typed=True, expire=60*60)
def get_global_features(atlas_id, parcellation_id, modality_id):
    if modality_id not in feature_classes:
        # modality_id not found in feature_classes
        raise HTTPException(status_code=400, detail=f'{modality_id} is not a valid modality')
    
    if not issubclass(feature_classes[modality_id], feature_export.GlobalFeature):
        # modality_id is not a global feature, return empty array
        return []

    atlas = create_atlas(atlas_id)
    # select atlas parcellation
    atlas.select_parcellation(parcellation_id)
    got_features = atlas.get_features(modality_id)
    if feature_classes[modality_id] == connectivity_export.ConnectivityMatrix:
        return [{
            '@id': f.src_name,
            'src_name': f.src_name,
            'src_info': f.src_info,
            'column_names': f.column_names,
            'matrix': f.matrix.tolist(),
        } for f in got_features]
    logger.info(f'feature {modality_id} has not yet been implemented')
    raise HTTPException(status_code=204, detail=f'feature {modality_id} has not yet been implemented')


def get_path_to_regional_map(query_id, roi, space_of_interest):

    regional_map = roi.get_regional_map(space_of_interest, siibra_commons.MapType.CONTINUOUS)
    if regional_map is None:
        raise HTTPException(status_code=404, detail=f'continuous regional map for region {roi.name} cannot be found')
    
    cached_filename = str(hashlib.sha256(query_id.encode('utf-8')).hexdigest()) + '.nii.gz'

    # cache fails, fetch from source
    def save_new_nii(cached_fullpath):
        import nibabel as nib
        # fix regional_map if necessary
        regional_map.image.header.set_xyzt_units('mm', 'sec')

        # time series
        regional_map.image.header['dim'][4] = 1

        # num channel
        regional_map.image.header['dim'][5] = 1
        nib.save(regional_map.image, cached_fullpath)
        
    return get_cached_file(cached_filename, save_new_nii)


# using a custom encoder is necessary to avoid cyclic reference
def vol_src_sans_space(vol_src):
    keys = ['id', 'name', 'url', 'volume_type', 'detail']
    return {
        key: getattr(vol_src, key) for key in keys
    }


siibra_custom_json_encoder={
    VolumeSrc: vol_src_sans_space,
    NiftiVolume: vol_src_sans_space,
    NgVolume: vol_src_sans_space,
}
