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
from app.configuration.diskcache import CACHEDIR

# TODO: Local or Remote NiftiVolume? NeuroglancerVolume = NgVolume?

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

