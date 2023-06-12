from api.common import data_decorator, get_filename, NotFound
from api.models.volumes.volume import MapType
from api.siibra_api_config import ROLE
from typing import Union

@data_decorator(ROLE)
def get_map(parcellation_id: str, space_id: str, maptype: Union[MapType, str]):
    import siibra
    from api.serialization.util import instance_to_model

    maptype_string = None
    # check maptype name and value both matches
    if isinstance(maptype, MapType):
        assert maptype.name == maptype.value, f"str enum, expecting .name and .value to equal"
        maptype_string = maptype.name
    if isinstance(maptype, str):
        maptype_string = maptype
    
    assert maptype_string is not None, f"maptype is neither MapType nor str"
    
    siibra_maptype = siibra.MapType[maptype_string]
    assert siibra_maptype.name == maptype_string, f"Expecting maptype.name to match"

    returned_map = siibra.get_map(parcellation_id, space_id, siibra_maptype)
    
    if returned_map is None:
        raise NotFound
    
    return instance_to_model(
        returned_map
    ).dict()


def cache_region_statistic_map(parcellation_id: str, region_id: str, space_id: str):
    import os
    full_filename = get_filename("statistical_map", parcellation_id, region_id, space_id, ext=".nii.gz")
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
    import json
    import time
    with open(f"{full_filename}.{str(int(time.time()))}.json", "w") as fp:
        json.dump({
            "prefix": "statistical_map",
            "parcellation_id": parcellation_id,
            "region_id": region_id,
            "space_id": space_id,
        }, fp=fp, indent="\t")
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
def get_parcellation_labelled_map(parcellation_id: str, space_id: str, region_id:str=None):
    import os
    full_filename = get_filename("labelled_map", parcellation_id, space_id, region_id if region_id else "", ext=".nii.gz")
    if os.path.isfile(full_filename):
        return full_filename

    import siibra
    import nibabel as nib
    error_text = f"Map with parc id '{parcellation_id}', space id '{space_id}'"

    volume_data = None
    if region_id is not None:
        region = siibra.get_region(parcellation_id, region_id)
        volume_data = region.fetch_regional_map(space_id, siibra.MapType.LABELLED)
    else:
        labelled_map = siibra.get_map(parcellation_id, space_id, siibra.MapType.LABELLED)
        assert labelled_map is not None, f"{error_text} returns None"
        volume_data = labelled_map.fetch()

    assert isinstance(volume_data, nib.Nifti1Image), f"{error_text}, volume provided is not of type Nifti1Image"
    
    nib.save(volume_data, full_filename)
    import json
    import time
    with open(f"{full_filename}.{str(int(time.time()))}.json", "w") as fp:
        json.dump({
            "prefix": "labelled_map",
            "parcellation_id": parcellation_id,
            "space_id": space_id,
            "region_id": region_id,
        }, fp=fp, indent="\t")
    return full_filename

@data_decorator(ROLE)
def assign_point(parcellation_id: str, space_id: str, point: str, assignment_type: str, sigma_mm: float):
    import siibra
    from api.serialization.util import instance_to_model
    m = siibra.get_map(parcellation_id, space_id, assignment_type)
    p = siibra.Point(point, space=space_id, sigma_mm=sigma_mm)
    df = m.assign(p)
    
    try:
        return instance_to_model(df, detail=True).dict()
    except Exception as e:
        raise e
    