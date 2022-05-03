# Copyright 2018-2022 Institute of Neuroscience and Medicine (INM-1),
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

from typing import List, Optional
import nibabel as nib
import hashlib
import os
from fastapi import HTTPException


from app.configuration.cache_redis import CacheRedis
from app.configuration.diskcache import CACHEDIR
from app.models import SPyParcellationFeature

import siibra
from siibra.core import Region, Parcellation, Space, BoundingBox
from siibra.core.serializable_concept import JSONSerializable
from siibra.features import FeatureQuery, modalities
from siibra.features.voi import VolumeOfInterest
from siibra.features.feature import RegionalFeature, ParcellationFeature, SpatialFeature


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


def get_all_vois():
    queries = FeatureQuery.queries("volume")
    features: List[VolumeOfInterest] = [feat for query in queries for feat in query.features]
    return features


all_voi_features = get_all_vois()


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

    image = regional_map.image

    # cache fails, fetch from source
    def save_new_nii(cached_fullpath):
        import nibabel as nib
        import numpy as np

        # fix regional_map if necessary
        image.header.set_xyzt_units('mm', 'sec')

        # time series
        image.header['dim'][4] = 1

        # num channel
        image.header['dim'][5] = 1

        # cast type float64 to float32
        if image.header.get_data_dtype() == np.float64:
            fdata=image.get_fdata()
            new_data=fdata.astype(np.float32)
            image.set_data_dtype(np.float32)

            if image.header['sizeof_hdr'] == 348:
                new_image=nib.Nifti1Image(new_data, image.affine, image.header)
            elif image.header['sizeof_hdr'] == 540:
                new_image=nib.Nifti2Image(new_data, image.affine, image.header)
            else:
                raise IOError('regional map has incorrect sizeof_hdr')
            nib.save(new_image, cached_fullpath)
        else:
            nib.save(image, cached_fullpath)

    return get_cached_file(cached_filename, save_new_nii)


def get_all_serializable_regional_features(region: Region, space: Space=None) -> List[RegionalFeature]:
    supported_modalities: List[str] = []
    for modality, query_list in [(modality, FeatureQuery._implementations[modality]) for modality in modalities]:
        if all(
            issubclass(query._FEATURETYPE, RegionalFeature) and
            issubclass(query._FEATURETYPE, JSONSerializable)
            for query in query_list
        ):
            supported_modalities.append(modality)

    # providing list/tuple to modality results in a dict return, rather than list
    return [feat
        for mod in supported_modalities
        for feat in siibra.get_features(region, modality=mod, space=space)]


def get_all_serializable_parcellation_features(parcellation: Parcellation, **kwargs) -> List[SPyParcellationFeature]:
    
    supported_modalities: List[str] = []
    for modality, query_list in [(modality, FeatureQuery._implementations[modality]) for modality in modalities]:
        if all(
            issubclass(query._FEATURETYPE, ParcellationFeature) and
            issubclass(query._FEATURETYPE, JSONSerializable)
            for query in query_list
        ):
            supported_modalities.append(modality)

    # providing list/tuple to modality results in a dict return, rather than list
    return [feat
        for mod in supported_modalities
        for feat in siibra.get_features(parcellation, modality=mod, **kwargs)]

def get_all_serializable_spatial_features(space: Space, parcellation: Parcellation=None, region: Region=None, bbox:BoundingBox=None, **kwargs):

    supported_modalities = []
    for modality, query_list in [(modality, FeatureQuery._implementations[modality]) for modality in modalities]:
        if all(
            issubclass(query._FEATURETYPE, SpatialFeature) and
            issubclass(query._FEATURETYPE, JSONSerializable)
            for query in query_list
        ):
            supported_modalities.append(modality)

    roi = region or parcellation
    if roi:
        return [feat
            for mod in supported_modalities
            for feat in siibra.get_features(roi, modality=mod, **kwargs)]
    if bbox:
        return [feat
            for feat in all_voi_features
            if feat.location.space is space and
            bbox.intersection(feat.location) ]
    raise HTTPException(
        status_code=400,
        detail=f"parcellation, region or bbox are required"
    )

def pagination_common_params(per_page: Optional[int] = 20, page: Optional[int] = 0):
    return {
        'per_page': per_page,
        'page': page,
    }
