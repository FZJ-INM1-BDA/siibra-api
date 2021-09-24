# Copyright 2018-2020 Institute of Neuroscience and Medicine (INM-1),
# Forschungszentrum Jülich GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import siibra
import nibabel as nib
from fastapi import HTTPException, Request
from app.configuration.cache_redis import CacheRedis
import anytree
import hashlib
import os
from app.configuration.diskcache import fanout_cache, CACHEDIR
from app import logger
from app.service.validation import validate_and_return_atlas
# TODO: Local or Remote NiftiVolume? NeuroglancerVolume = NgVolume?
from siibra.volumes.volume import VolumeSrc, LocalNiftiVolume, NeuroglancerVolume

cache_redis = CacheRedis.get_instance()


def create_region_json_response(region, space_id=None, atlas=None, detail=False):
    region_json = _create_region_json_object(region, space_id, atlas, detail)
    _add_children_to_region(region_json, region, space_id, atlas)
    return region_json


def _add_children_to_region(region_json, region, space_id=None, atlas=None):
    for child in region.children:
        o = _create_region_json_object(child)
        # if space_id is not None and atlas is not None:
        #     get_region_props_tmp(space_id, atlas, o, child)
        if child.children:
            _add_children_to_region(o, child, space_id, atlas)
        region_json['children'].append(o)


def _create_region_json_object(region, space_id=None, atlas=None, detail=False):
    region_json = {'name': region.name, 'children': []}
    if hasattr(region, 'rgb'):
        region_json['rgb'] = region.rgb
    if hasattr(region, 'fullId'):
        region_json['id'] = region.fullId
    if hasattr(region, 'labelIndex'):
        region_json['labelIndex'] = region.labelIndex
    if hasattr(region, 'attrs'):
        region_json['volumeSrc'] = region.attrs.get('volumeSrc', {})
    if detail and hasattr(region, 'origin_datainfos'):
        region_json['originDatainfos'] = [origin_data_decoder(datainfo) for datainfo in region.origin_datainfos]
    region_json['availableIn'] = get_available_spaces_for_region(region)

    if detail:
        #TODO new way to check for regional map
        # region_json['hasRegionalMap'] = region.has_regional_map(
        #     siibra.spaces[space_id],
        #     bs.commons.MapType.CONTINUOUS) if space_id is not None else None
        region_json['hasRegionalMap'] = None
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


def get_spaces_for_parcellation(parcellation):
    return [space for space in siibra.spaces if parcellation.supports_space(space)]


def get_parcellations_for_space(space):
    return [{'id': parcellation.id, 'name': parcellation.name}
            for parcellation in siibra.parcellations if parcellation.supports_space(space)]


def get_base_url_from_request(request: Request):
    proto_header = 'x-forwarded-proto'
    proto = 'http'
    host = request.headers.get('host')
    api_version = str(request.url).replace(
        str(request.base_url), '').split('/')[0]
    if proto_header in request.headers:
        proto = request.headers.get(proto_header)

    return '{}://{}/{}/'.format(proto, host, api_version)


def get_available_spaces_for_region(region):
    result = []
    for spaces in siibra.spaces:
        if region.parcellation.supports_space(spaces):
            result.append(_object_to_json(spaces))
    return result


def get_region_props(space_id, atlas, region) -> list:
    space = atlas.get_space(space_id)
    try:
        logger.info(f'Getting region props for: {region}')
        result_props = region.spatialprops(space, force=True)
    except:
        logger.info(f'Could not get region properties for region: {region} and space: {space}')
        result_props = []
    return result_props


# def get_region_props_tmp(space_id, atlas, region_json, region):
#     logger.debug('Getting props for: {}'.format(str(region)))
#     region_json['props'] = {}
    # cache_value = cache_redis.get_value('{}_{}_{}_{}'.format(
    #     str(atlas.id),
    #     str(atlas.selected_parcellation.id),
    #     str(find_space_by_id(atlas, space_id).id),
    #     str(region)
    # ))
    # reg_props = region.spatialprops(find_space_by_id(atlas,space_id), force=True)
    # print(reg_props)
    # if cache_value == 'invalid' or cache_value == 'None' or cache_value is None:
    #     region_json['props']['centroid_mm'] = ''
    #     region_json['props']['volume_mm'] = ''
    #     region_json['props']['surface_mm'] = ''
    #     region_json['props']['is_cortical'] = ''
    # else:
    #     r_props = json.loads(cache_value)
    #     region_json['props']['centroid_mm'] = r_props['centroid_mm']
    #     region_json['props']['volume_mm'] = r_props['volume_mm']
    #     region_json['props']['surface_mm'] = r_props['surface_mm']
    #     region_json['props']['is_cortical'] = r_props['is_cortical']


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

    fuzzy_regions = atlas.find_regions(region_id)

    region_tree = atlas.selected_parcellation.regiontree
    strict_equal_id = anytree.search.findall(region_tree, match_node)
    return [*strict_equal_id, *fuzzy_regions]


# allow for fast fails
SUPPORTED_FEATURES = [
    # siibra.features.genes.GeneExpression,
    siibra.features.genes.AllenBrainAtlasQuery,
    siibra.features.connectivity.ConnectivityProfileQuery,
    siibra.features.receptors.ReceptorQuery,
    siibra.features.ebrains.EbrainsRegionalFeatureQuery,
    siibra.features.ieeg.IEEG_SessionQuery]


@fanout_cache.memoize(typed=True)
def get_regional_feature(
        atlas_id,
        parcellation_id,
        region_id,
        modality_id,
        detail=True,
        feature_id=None,
        gene=None):
    if not siibra.modalities.provides(modality_id):#feature_classes:
        # modality_id not found in feature_classes
        raise HTTPException(status_code=400,
                            detail=f'{modality_id} is not a valid modality')

    # fail fast if not in supported feature list
    # if siibra.modalities[modality_id] not in SUPPORTED_FEATURES:
    #     raise HTTPException(
    #         status_code=501,
    #         detail=f'feature {modality_id} has not yet been implemented')

# TODO - check for subclass
#     if not issubclass(
#             feature_classes[modality_id],
#             feature_export.RegionalFeature):
#         # modality_id is not a global feature, return empty array
#         return []

    atlas = validate_and_return_atlas(atlas_id)
    parcellation = atlas.get_parcellation(parcellation_id)
    region = atlas.get_region(region_id, parcellation)

    # TODO: validate region
    #     raise HTTPException(status_code=404,
    #                         detail=f'Region with id {region_id} not found!')
    try:
        got_features = siibra.get_features(region, modality_id)
    except:
        raise HTTPException(
                     status_code=500,
                     detail=f'Could not get features for region with id {region_id}')

    shaped_features = None
    if siibra.features.modalities[modality_id] == siibra.features.ebrains.EbrainsRegionalFeatureQuery:
        shaped_features = [{
            'summary': {
                '@id': kg_rf_f.id,
                'src_name': kg_rf_f.name,
            },
            'get_detail': lambda kg_rf_f: { '__detail': kg_rf_f.detail },
            'instance': kg_rf_f,
        } for kg_rf_f in got_features]
    if siibra.features.modalities[modality_id] == siibra.features.genes.AllenBrainAtlasQuery:
        shaped_features = [{
            'summary': {
                '@id': hashlib.md5(str(gene_feat).encode("utf-8")).hexdigest(),
            },
            'get_detail': lambda gene_feat : { 
                '__donor_info': gene_feat.donor_info,
                '__gene': gene_feat.gene,
                '__probe_ids': gene_feat.probe_ids,
                '__mri_coord': gene_feat.mri_coord,
                '__z_scores': gene_feat.z_scores,
                '__expression_levels': gene_feat.expression_levels
             },
             'instance': gene_feat,
        } for gene_feat in got_features]
    if siibra.features.modalities[modality_id] == siibra.features.connectivity.ConnectivityProfileQuery:
        shaped_features = [{
            'summary': {
                "@id": conn_pr._matrix.id,
                "src_name": conn_pr.name,
                "src_info": conn_pr.description,
                "kgSchema": conn_pr._matrix.type_id,
                "kgId": conn_pr._matrix.id,
            },
            'get_detail': lambda conn_pr: { 
                # "__column_names": conn_pr.column_names, TODO: where to get the names?
                "__profile": conn_pr.profile.tolist(),
             },
             'instance': conn_pr,
        } for conn_pr in got_features]
    if siibra.features.modalities[modality_id] == siibra.features.receptors.ReceptorQuery:
        shaped_features = [{
            'summary': {
                "@id": receptor_pr.name,
                "name": receptor_pr.name,
                "info": receptor_pr.info,
                "origin_datainfos": [{
                    'name': receptor_pr.name,
                    'description': receptor_pr.info,
                    'urls': [{
                        'doi': receptor_pr.url
                    }]
                }]
            },
            'get_detail': lambda receptor_pr: { 
                "__receptor_symbols": siibra.features.receptors.RECEPTOR_SYMBOLS,
                "__files": receptor_pr.files,
                "__data": {
                    "__profiles": receptor_pr.profiles,
                    "__autoradiographs": receptor_pr.autoradiographs,
                    "__fingerprint": receptor_pr.fingerprint,
                    "__profile_unit": receptor_pr.profile_unit,
                },
             },
             'instance': receptor_pr,
        } for receptor_pr in got_features]

    if shaped_features is None:
        raise HTTPException(
            status_code=501,
            detail=f'feature {modality_id} has not yet been implmented')

    if feature_id is not None:
        shaped_features = [ f for f in shaped_features if f['summary']['@id'] == feature_id]
    return [{
        **f['summary'],
        **(f['get_detail'](f['instance']) if detail else {})
    } for f in shaped_features ]


@fanout_cache.memoize(typed=True)
def get_global_features(atlas_id, parcellation_id, modality_id):
    if modality_id not in siibra.features.modalities:
    # if modality_id not in feature_classes:
        # modality_id not found in feature_classes
        raise HTTPException(status_code=400,
                            detail=f'{modality_id} is not a valid modality')

    #TODO check if still needed
    # if not issubclass(
    #         feature_classes[modality_id],
    #         feature_export.GlobalFeature):
    #     # modality_id is not a global feature, return empty array
    #     return []

    atlas = siibra.atlases[atlas_id]
    parcellation = atlas.get_parcellation(parcellation_id)

    got_features = siibra.get_features(parcellation, modality_id)
    if siibra.features.modalities[modality_id] == siibra.features.connectivity.ConnectivityMatrixQuery:
        return [{
            '@id': f.id,
            'src_name': f.name,
            'src_info': f.description,
            # 'column_names': f.column_names, TODO: Where to get column names
            'matrix': f.matrix.tolist(),
        } for f in got_features]
    logger.info(f'feature {modality_id} has not yet been implemented')
    raise HTTPException(
        status_code=204,
        detail=f'feature {modality_id} has not yet been implemented')


def get_contact_pt_detail(contact_pt, atlas=None, parc_id=None):
    return {
        'id': contact_pt.id,
        'location': contact_pt.location,
        **({'inRoi': contact_pt.matches(atlas)} if parc_id is not None and atlas is not None else {})
    }


def get_electrode_detail(electrode, atlas=None, parc_id=None):
    return {
        'electrode_id': electrode.electrode_id,
        'subject_id': electrode.subject_id,
        'contact_points': {
            contact_pt_id: get_contact_pt_detail(electrode.contact_points[contact_pt_id], atlas, parc_id)
            for contact_pt_id in electrode.contact_points},
        **({'inRoi': electrode.matches(atlas)} if parc_id is not None and atlas is not None else {})
    }


@fanout_cache.memoize(typed=True)
def get_spatial_features(atlas_id, space_id, modality_id, feature_id=None, detail=False, parc_id=None, region_id=None):

    space_of_interest = siibra.spaces[space_id]
    if space_of_interest is None:
        raise HTTPException(404, detail=f'space with id {space_id} cannot be found')

    if modality_id not in siibra.features.modalities:
        raise HTTPException(status_code=400,
                            detail=f'{modality_id} is not a valid modality')

    # TODO: Check if this is still needed or can be replaced
    # fail fast if not in supported feature list
    # if siibra.features.modalities[modality_id] not in SUPPORTED_FEATURES:
    # if feature_classes[modality_id] not in SUPPORTED_FEATURES:
    #     raise HTTPException(
    #         status_code=501,
    #         detail=f'feature {modality_id} has not yet been implmented')

    # TODO: Why only spatial features
    if not issubclass(
            # feature_classes[modality_id],
            # feature_export.SpatialFeature):
            siibra.features.modalities[modality_id]._FEATURETYPE,
            siibra.features.feature.SpatialFeature):
        # modality_id is not a global feature, return empty array
        return []

    # select atlas by id
    atlas = siibra.atlases[atlas_id]
    if space_of_interest not in atlas.spaces:
        raise HTTPException(404, detail=f'space {space_id} not in atlas {atlas}')

    # TODO: No Selection of parcellation and region is needed - TODO: How to provide parcellation/region
    if parc_id:
        if region_id is None:
            raise HTTPException(status_code=400, detail='region is needed, if parc_id is provided')
        # atlas.select_parcellation(parc_id)
        # atlas.select_region(region_id)

    try:
        # spatial_features=atlas.get_features(modality_id)
        spatial_features = siibra.get_features(space_of_interest, modality_id)
    except Exception:
        raise HTTPException(404, detail=f'Could not get spatial features.')
    #TODO: Result is empty, why?
    filtered_features = [f for f in spatial_features if f.space == space_of_interest]
    shaped_features = None
    if siibra.features.modalities[modality_id] == siibra.features.ieeg.IEEG_SessionQuery:
    # if feature_classes[modality_id] == ieeg_export.IEEG_Electrode:
        shaped_features=[{
            'summary': {
                '@id': hashlib.md5(str(feat).encode("utf-8")).hexdigest(),
                'name': str(feat),
                'origin_datainfos': [{
                    'urls': [{
                        'doi': f'https://search.kg.ebrains.eu/instances/{feat.kg_id}'
                    }]
                }]
            },
            'get_detail': lambda ft: get_electrode_detail(ft,
                atlas=atlas,
                parc_id=parc_id),
            'instance': feat
        } for feat in filtered_features]

    #TODO Check what to do with this Dataset
    # if siibra.features.modalities[modality_id] == siibra.features.ieeg.IEEG_Dataset:
    # # if feature_classes[modality_id] == ieeg_export.IEEG_Dataset:
    #     shaped_features=[{
    #         'summary': {
    #             '@id': hashlib.md5(str(feat).encode("utf-8")).hexdigest(),
    #             'name': feat.name,
    #             'description': feat.description,
    #             'origin_datainfos': [{
    #                 'urls': [{
    #                     'doi': f'https://search.kg.ebrains.eu/instances/{feat.kg_id}'
    #                 }]
    #             }]
    #         },
    #         'get_detail': lambda ft: {
    #             'kg_id': ft.kg_id,
    #             'electrodes': {
    #                 subject_id: {
    #                     electrode_id: get_electrode_detail(
    #                         ft.electrodes[subject_id][electrode_id],
    #                         atlas=atlas,
    #                         parc_id=parc_id,
    #                     ) for electrode_id in ft.electrodes[subject_id]
    #                 } for subject_id in ft.electrodes
    #             }
    #         },
    #         'instance': feat
    #     } for feat in filtered_features]
    if shaped_features is None:
        raise HTTPException(501, detail=f'{modality_id} not yet implemented')

    if feature_id is not None:
        shaped_features=[f for f in shaped_features if f['summary']['@id'] == feature_id]

    return [{
        **f['summary'],
        **(f['get_detail'](f['instance']) if detail else {}),
    } for f in shaped_features]

def get_path_to_regional_map(query_id, roi, space_of_interest):

    regional_map = roi.get_regional_map(
        space_of_interest, siibra.commons.MapType.CONTINUOUS)
    if regional_map is None:
        raise HTTPException(
            status_code=404,
            detail=f'continuous regional map for region {roi.name} cannot be found')

    cached_filename = str(
        hashlib.sha256(
            query_id.encode('utf-8')).hexdigest()) + '.nii.gz'

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

def origin_data_decoder(origin_data):
    description=origin_data.description
    name=origin_data.name
    urls=origin_data.urls
    return {'name': name,
        'description': description,
        'urls': urls}


siibra_custom_json_encoder = {
    VolumeSrc: vol_src_sans_space,
    LocalNiftiVolume: vol_src_sans_space,
    NeuroglancerVolume: vol_src_sans_space,
}
