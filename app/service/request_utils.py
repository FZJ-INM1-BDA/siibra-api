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

import nibabel as nib
from fastapi import Request
from app.configuration.cache_redis import CacheRedis
import os
from app.configuration.diskcache import CACHEDIR

cache_redis = CacheRedis.get_instance()


def get_cached_file_path(filename: str, fn: callable) -> str:
    """
    Get full path to a cached file. Pseudo diskcache, but for files.

    Usage
    ------
    In the example below, `create_nifti` will only be called once.
    ```python
    def create_nifti(full_path):
        # expensive calls
        import nibabel as nib
        nib.save(SOMEDATA, full_path)

    path_to_expensive_nii = get_cached_file_path('expensive.nii.gz', create_nifti)
    
    # some time later

    path_to_expensive_nii_again = get_cached_file_path('expensive.nii.gz', create_nifti)
    ```


    Parameters
    ------
    filename: str
        Filename (including extension) of the file
    
    fn: callable
        Function that will be called if the file with the filename does not yet exist.
        Typically, this is a good place to perform any expensive calls that generate the file,
        so subsequent calls can hit the file on disk directly.

        the callable takes 1 (one) argument, cached_full_path.

    Returns
    ------
    cached_full_path: str
        Path to the cached file.
    """
    cached_full_path = os.path.join(CACHEDIR, filename)

    # if path does not exist, call the provided fn
    if not os.path.exists(cached_full_path):
        fn(cached_full_path)

    return cached_full_path


# TODO remove? use environ HOSTURL instead?
def get_base_url_from_request(request: Request):
    proto_header = 'x-forwarded-proto'
    proto = 'http'
    host = request.headers.get('host')
    api_version = str(request.url).replace(
        str(request.base_url), '').split('/')[0]
    if proto_header in request.headers:
        proto = request.headers.get(proto_header)

    return '{}://{}/{}/'.format(proto, host, api_version)


def fix_nii_for_neuroglancer(nii):
    """
    Returns a nii object that can be properly. 

    Parameters:
        nii: nibabel image object

    Returns:
        nii: nibabel image object
    """
    import nibabel as nib
    import numpy as np

    # fix regional_map if necessary
    nii.header.set_xyzt_units('mm', 'sec')

    # time series
    nii.header['dim'][4] = 1

    # num channel
    nii.header['dim'][5] = 1

    # cast type float64 to float32
    if nii.header.get_data_dtype() == np.float64:
        fdata=nii.get_fdata()
        new_data=fdata.astype(np.float32)
        nii.set_data_dtype(np.float32)

        if nii.header['sizeof_hdr'] == 348:
            new_image=nib.Nifti1Image(new_data, nii.affine, nii.header)
        elif nii.header['sizeof_hdr'] == 540:
            new_image=nib.Nifti2Image(new_data, nii.affine, nii.header)
        else:
            raise IOError('regional map has incorrect sizeof_hdr')
        return new_image
    else:
        return nii
