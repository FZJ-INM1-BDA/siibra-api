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
import hashlib
import os
from app.configuration.diskcache import memoize, CACHEDIR
from app import logger
from app.service.validation import validate_and_return_atlas, validate_and_return_parcellation, \
    validate_and_return_region, validate_and_return_space
# TODO: Local or Remote NiftiVolume? NeuroglancerVolume = NgVolume?
from siibra.volumes.volume import VolumeSrc, LocalNiftiVolume, NeuroglancerVolume

cache_redis = CacheRedis.get_instance()

def get_file_from_nibabel(nibabel_object, nifti_type, space):
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


def get_base_url_from_request(request: Request):
    proto_header = 'x-forwarded-proto'
    proto = 'http'
    host = request.headers.get('host')
    api_version = str(request.url).replace(
        str(request.base_url), '').split('/')[0]
    if proto_header in request.headers:
        proto = request.headers.get(proto_header)

    return '{}://{}/{}/'.format(proto, host, api_version)


# allow for fast fails
SUPPORTED_FEATURES = [
    # siibra.features.genes.GeneExpression,
    siibra.features.genes.AllenBrainAtlasQuery,
    siibra.features.connectivity.ConnectivityProfileQuery,
    siibra.features.receptors.ReceptorQuery,
    siibra.features.ebrains.EbrainsRegionalFeatureQuery,
    siibra.features.ieeg.IEEG_SessionQuery]


@memoize(typed=True)
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

    # TODO - check for subclass
    #     if not issubclass(
    #             feature_classes[modality_id],
    #             feature_export.RegionalFeature):
    #         # modality_id is not a global feature, return empty array
    #         return []

    atlas = validate_and_return_atlas(atlas_id)
    parcellation = validate_and_return_parcellation(parcellation_id)
    # region = atlas.get_region(region_id, parcellation)
    region = validate_and_return_region(region_id, parcellation)

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
                "__column_names": list(conn_pr.regionnames), #TODO: where to get the names?
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
                "__files": [], #receptor_pr.files, # TODO where  to get files
                "__data": {
                    "__profiles": receptor_pr.profiles,
                    "__autoradiographs": {},
                    "__fingerprint": receptor_pr.fingerprint,
                    # "__profile_unit": receptor_pr.profile_unit, TODO check where to get units
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


@memoize(typed=True)
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


def get_contact_pt_detail(contact_pt: siibra.features.ieeg.IEEG_ContactPoint, region: siibra.core.Region, **kwargs):
    return {
        'id': contact_pt.id,
        'location': list(contact_pt.location),
        **({'inRoi': contact_pt.match(region)} if region is not None else {})
    }

def get_electrode_detail(electrode: siibra.features.ieeg.IEEG_Electrode, region: siibra.core.Region, **kwargs):
    return {
        'electrode_id': electrode.electrode_id,
        'subject_id': electrode.session.sub_id,
        'contact_points': {
            contact_pt_id: get_contact_pt_detail(
                electrode.contact_points[contact_pt_id],
                region=region,
                **kwargs)
            for contact_pt_id in electrode.contact_points },
        **({'inRoi': electrode.match(region)} if region is not None else {})
    }

def get_ieeg_session_detail(ieeg_session: siibra.features.ieeg.IEEG_Session, region: siibra.core.Region, **kwargs):
    
    return {
        'sub_id': ieeg_session.sub_id,
        'electrodes': {
            electrode_key: get_electrode_detail(ieeg_session.electrodes[electrode_key],
                region=region,
                **kwargs)
            for electrode_key in ieeg_session.electrodes},
        **({'inRoi': ieeg_session.match(region)} if region is not None else {})
    }

@memoize(typed=True)
def get_spatial_features(atlas_id, space_id, modality_id, feature_id=None, detail=False, parc_id=None, region_id=None):

    space_of_interest = validate_and_return_space(space_id)

    if modality_id not in siibra.features.modalities:
        raise HTTPException(status_code=400,
                            detail=f'{modality_id} is not a valid modality')

    # TODO: Why only spatial features
    if not issubclass(
            # feature_classes[modality_id],
            # feature_export.SpatialFeature):
            siibra.features.modalities[modality_id]._FEATURETYPE,
            siibra.features.feature.SpatialFeature):
        # modality_id is not a global feature, return empty array
        return []

    atlas = validate_and_return_atlas(atlas_id)
    # TODO not working at the moment. Space_of_interest is never in atlas.spaces
    # if space_of_interest not in atlas.spaces:
    #     raise HTTPException(404, detail=f'space {space_id} not in atlas {atlas}')

    # TODO: No Selection of parcellation and region is needed - TODO: How to provide parcellation/region
    if parc_id is None:
        raise HTTPException(status_code=400, detail='Parc id is needed')
    
    parc=validate_and_return_parcellation(parc_id)
    roi=validate_and_return_region(region_id, parc)

    try:
        # spatial_features=atlas.get_features(modality_id)
        spatial_features = siibra.get_features(roi, modality_id, space=space_of_interest)
    except Exception:
        raise HTTPException(404, detail=f'Could not get spatial features.')
    
    shaped_features = None
    if siibra.features.modalities[modality_id] == siibra.features.ieeg.IEEG_SessionQuery:
        shaped_features=[{
            'summary': {
                '@id': hashlib.md5(str(feat).encode("utf-8")).hexdigest(),
                'name': f'{feat.dataset.name} sub:{feat.sub_id}',
                'description': str(feat.dataset.description),
                'origin_datainfos': [{
                    'urls': feat.dataset.urls
                }]
            },
            'get_detail': lambda ft: get_ieeg_session_detail(ft,
                region=roi,
                parcellation=parc,
                space=space_of_interest,
                atlas=atlas),
            'instance': feat
        } for feat in spatial_features]

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
        import numpy as np

        # fix regional_map if necessary
        regional_map.image.header.set_xyzt_units('mm', 'sec')

        # time series
        regional_map.image.header['dim'][4] = 1

        # num channel
        regional_map.image.header['dim'][5] = 1

        # cast type float64 to float32
        if regional_map.image.header.get_data_dtype() == np.float64:
            fdata=regional_map.image.get_fdata()
            new_data=fdata.astype(np.float32)
            regional_map.image.set_data_dtype(np.float32)

            if regional_map.image.header['sizeof_hdr'] == 348:
                new_image=nib.Nifti1Image(new_data, regional_map.image.affine, regional_map.image.header)
            elif regional_map.image.header['sizeof_hdr'] == 540:
                new_image=nib.Nifti2Image(new_data, regional_map.image.affine, regional_map.image.header)
            else:
                raise IOError('regional map has incorrect sizeof_hdr')
            nib.save(new_image, cached_fullpath)
        else:
            nib.save(regional_map.image, cached_fullpath)

    return get_cached_file(cached_filename, save_new_nii)

# using a custom encoder is necessary to avoid cyclic reference
def vol_src_sans_space(vol_src):
    keys = ['id', 'name', 'url', 'volume_type', 'detail']
    return {
        key: getattr(vol_src, key) for key in keys
    }

def density_profile_encoder(density: siibra.features.receptors.DensityProfile):
    return density.densities

def receptor_profile_encoder(receptor: siibra.features.receptors.ReceptorDistribution):
    return {
        '__data': {
            '__profiles': {
                profile_key: receptor.profiles[profile_key]
                for profile_key in receptor.profiles}
        }
    }

siibra_custom_json_encoder = {
    VolumeSrc: vol_src_sans_space,
    LocalNiftiVolume: vol_src_sans_space,
    NeuroglancerVolume: vol_src_sans_space,
    siibra.features.receptors.DensityProfile: density_profile_encoder,
    siibra.features.receptors.ReceptorDistribution: receptor_profile_encoder,
}
