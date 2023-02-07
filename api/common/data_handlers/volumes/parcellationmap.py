from api.common import data_decorator, get_filename
from api.models.volumes.volume import MapType
from api.siibra_api_config import ROLE

@data_decorator(ROLE)
def get_map(parcellation_id: str, space_id: str, maptype: MapType):
    import siibra
    from api.serialization.util import instance_to_model

    # check maptype name and value both matches
    assert maptype.name == maptype.value, f"str enum, expecting .name and .value to equal"
    siibra_maptype = siibra.MapType[maptype.name]
    assert siibra_maptype.name == maptype.name, f"Expecting maptype.name to match"

    return instance_to_model(
        siibra.get_map(parcellation_id, space_id, siibra_maptype)
    ).dict()


def cache_region_statistic_map(parcellation_id: str, region_id: str, space_id: str):
    import os
    full_filename = get_filename(parcellation_id, region_id, space_id, ext=".nii.gz")
    if os.path.isfile(full_filename):
        return full_filename

    import siibra
    import nibabel as nib
    error_text = f"Map with parc id '{parcellation_id}', space id '{space_id}'"

    stat_map = siibra.get_map(parcellation_id, space_id, siibra.MapType.STATISTICAL)
    assert stat_map is not None, f"{error_text} returns None"
    
    volume_data = stat_map.fetch(region=region_id)

    error_text = f"{error_text}, with region_id '{region_id}'"
    assert isinstance(volume_data, nib.Nifti1Image), f"{error_text}, volume provided is not of type Nifti1Image"
    
    nib.save(volume_data, full_filename)
    return full_filename

@data_decorator(ROLE)
def get_region_statistic_map(parcellation_id: str, region_id: str, space_id: str):
    return cache_region_statistic_map(parcellation_id, region_id, space_id)

@data_decorator(ROLE)
def get_region_statistic_map_info(parcellation_id: str, region_id: str, space_id: str):
    full_filename = cache_region_statistic_map(parcellation_id, region_id, space_id)
    
    import nibabel as nib
    import numpy as np
    
    nii = nib.load(full_filename)
    data = nii.get_fdata()
    return {
        "min": np.min(data),
        "max": np.max(data),
    }

@data_decorator(ROLE)
def get_parcellation_labelled_map(parcellation_id: str, space_id: str):
    import os
    full_filename = get_filename(parcellation_id, space_id, ext=".nii.gz")
    if os.path.isfile(full_filename):
        return full_filename

    import siibra
    import nibabel as nib
    error_text = f"Map with parc id '{parcellation_id}', space id '{space_id}'"

    labelled_map = siibra.get_map(parcellation_id, space_id, siibra.MapType.LABELLED)
    assert labelled_map is not None, f"{error_text} returns None"
    
    volume_data = labelled_map.fetch()
    assert isinstance(volume_data, nib.Nifti1Image), f"{error_text}, volume provided is not of type Nifti1Image"
    
    nib.save(volume_data, full_filename)
    return full_filename
