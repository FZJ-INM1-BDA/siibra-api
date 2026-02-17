from api.common import data_decorator, get_filename, NotFound
from api.models.volumes.volume import MapType
from api.siibra_api_config import ROLE
from typing import Union, Dict, Tuple, List

def parse_maptype(maptype: Union[MapType, str]):
    if isinstance(maptype, MapType):
        assert maptype.name == maptype.value, f"str enum, expecting .name and .value to equal"
        return maptype.name
    if isinstance(maptype, str):
        return maptype

@data_decorator(ROLE)
def get_map(parcellation_id: str, space_id: str, maptype: Union[MapType, str]) -> Dict:
    """Get a map instance, based on specification
    
    Args:
        parcellation_id: lookup id of the parcellation of the map
        space_id: lookup id of the space of the map
        maptype: maptype, either LABELLED or STATISTICAL
    
    Returns:
        Requested map instance, serialized into dict
    
    Raises:
        AssertionError: if the supplied maptype is invalid type
        NotFound: Map with the specification not found
    """
    import siibra
    from api.serialization.util import instance_to_model

    maptype_string = parse_maptype(maptype)
    
    assert maptype_string is not None, f"maptype is neither MapType nor str"
    
    siibra_maptype = siibra.MapType[maptype_string]
    assert siibra_maptype.name == maptype_string, f"Expecting maptype.name to match"

    returned_map = siibra.get_map(parcellation_id, space_id, siibra_maptype)
    
    if returned_map is None:
        raise NotFound
    
    return instance_to_model(
        returned_map, detail=True
    ).dict()


def cache_region_statistic_map(parcellation_id: str, region_id: str, space_id: str) -> Tuple[str, bool]:
    """Retrieve and save regional statistical map (if necessary), and then return the path of the map.

    Args:
        parcellation_id: lookup id of the parcellation of the map
        region_id: lookup id of the region of the map
        space_id: lookup id of the space of the map
    
    Returns:
        path to statistical map, if a cached file is returned
    """
    import os
    full_filename = get_filename("statistical_map", parcellation_id, region_id, space_id, ext=".nii.gz")
    if os.path.isfile(full_filename):
        return full_filename, True

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
    return full_filename, False

@data_decorator(ROLE)
def get_region_statistic_map(parcellation_id: str, region_id: str, space_id: str):
    """Retrieve and save regional statistical map (if necessary), and then return the path of the map.

    Args:
        parcellation_id: lookup id of the parcellation of the map
        region_id: lookup id of the region of the map
        space_id: lookup id of the space of the map
    
    Returns:
        path to statistical map, if a cached file is returned
    """
    return cache_region_statistic_map(parcellation_id, region_id, space_id)

@data_decorator(ROLE)
def get_region_statistic_map_info(parcellation_id: str, region_id: str, space_id: str):
    """Retrieve and save regional statistical map (if necessary), and then return the path of the map.

    Args:
        parcellation_id: lookup id of the parcellation of the map
        region_id: lookup id of the region of the map
        space_id: lookup id of the space of the map
    
    Returns:
        dict of min an max of the statistical map
    """
    full_filename, _cache_flag = cache_region_statistic_map(parcellation_id, region_id, space_id)
    
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
    """Retrieve and save labelled map / regional mask (if necessary), and then return the path of the map.

    Args:
        parcellation_id: lookup id of the parcellation of the map
        region_id: lookup id of the region of the map
        space_id: lookup id of the space of the map
    
    Returns:
        path to labelled map/regional mask, if a cached file is returned
    """
    import os
    full_filename = get_filename("labelled_map", parcellation_id, space_id, region_id if region_id else "", ext=".nii.gz")
    if os.path.isfile(full_filename):
        return full_filename, True

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
    return full_filename, False

# @data_decorator(ROLE)
# def assign_point(parcellation_id: str, space_id: str, point: str, assignment_type: str, sigma_mm: float):
#     import siibra
#     from api.serialization.util import instance_to_model
#     m = siibra.get_map(parcellation_id, space_id, assignment_type)
#     p = siibra.Point(point, space=space_id, sigma_mm=sigma_mm)
#     df = m.assign(p)
    
#     try:
#         return instance_to_model(df, detail=True).dict()
#     except Exception as e:
#         raise e

@data_decorator(ROLE)
def get_resampled_map(parcellation_id: str, space_id: str, name: str=None):
    """Retrieve and save a labelled map, resampled in space (if necessary), and then return the path of the map.

    Args:
        parcellation_id: lookup id of the parcellation of the map
        space_id: lookup id of the target space of the sampled map
    
    Returns:
        path to statistical map, if a cached file is returned
    """
    import os
    full_filename = get_filename("resampled_map", parcellation_id, space_id, name or "none", ext=".nii.gz")
    if os.path.isfile(full_filename):
        return full_filename, True
    
    import siibra
    import nibabel as nib
    parcellation: siibra.core.parcellation.Parcellation = siibra.parcellations[parcellation_id]
    parcellation_map = parcellation.get_map(siibra.spaces[space_id], siibra.MapType.LABELLED)
    if len(parcellation_map.fragments) > 0:
        nii = parcellation_map.get_resampled_template(fragment=name)
    else:
        nii = parcellation_map.get_resampled_template()

    assert isinstance(nii, nib.Nifti1Image), f"resample failed... returned not of type nii"
    
    import time
    import json
    nib.save(nii, full_filename)
    with open(f"{full_filename}.{str(int(time.time()))}.json", "w") as fp:
        json.dump({
            "prefix": "resampled_map",
            "parcellation_id": parcellation_id,
            "space_id": space_id,
        }, indent="\t", fp=fp)
    return full_filename, False


@data_decorator(ROLE)
def get_filtered_maps(parcellation_id: str=None, space_id: str=None, maptype: Union[MapType, str, None]=None):
    import siibra
    from api.serialization.util import instance_to_model

    return_arr: List[siibra._parcellationmap.Map] = []
    for mp in siibra.maps:
        mp: siibra._parcellationmap.Map = mp
        if (
            parcellation_id is not None
            and mp.parcellation.id != parcellation_id
        ):
            continue
        if (
            space_id is not None
            and mp.space.id != space_id
        ):
            continue
        if (
            maptype is not None
            and mp.maptype.name != parse_maptype(maptype)
        ):
            continue
        return_arr.append(mp)
    return [ instance_to_model(m).dict() for m in return_arr]


@data_decorator(ROLE)
def get_single_map(map_id: str):
    import siibra
    from api.serialization.util import instance_to_model
    for mp in siibra.maps:
        mp: siibra._parcellationmap.Map = mp
        if mp.id == map_id:
            return instance_to_model(mp, detail=True).dict()
    raise NotFound(f"map with id {map_id} not found.")
