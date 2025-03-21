try:
    from typing import Literal, List, Union
except ImportError:
    from typing import List, Union
    from typing_extensions import Literal

from new_api.data_handlers.maps import cache_region_statistic_map, cache_parcellation_labelled_map, cache_resampled_map
from new_api.v3.serialization import instance_to_model
from new_api.v3.models.volumes.volume import MapType
from new_api.common.exceptions import NotFound
from new_api.common.decorators import data_decorator
from new_api.siibra_api_config import ROLE
from new_api.common.logger import logger

from new_api.warmup import register_warmup_fn

@data_decorator(ROLE)
def assign(parcellation_id: str, space_id: str, point: str, assignment_type: str=Literal["statistical", "labelled"], sigma_mm: float=0., extra_specs: str=""):
    import siibra
    from siibra.attributes.locations.point import parse_coordinate, Point
    coordinate = parse_coordinate(point)
    point = Point(coordinate=coordinate, space_id=space_id, sigma=sigma_mm)
    maps = siibra.find_maps(parcellation_id, space_id, assignment_type, extra_specs)
    if len(maps) == 0:
        raise NotFound(f"map with {parcellation_id!r}, {space_id!r}, {assignment_type!r}, {extra_specs!r} not found")
    mp = maps[0]
    result = mp.lookup_points(point)
    return instance_to_model(result, detail=True).dict()

@data_decorator(ROLE)
def get_map(parcellation_id: str, space_id: str, maptype: Union[MapType, str], extra_spec: str=""):
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
    
    # check maptype name and value both matches
    if isinstance(maptype, MapType):
        assert maptype.name == maptype.value, f"str enum, expecting .name and .value to equal"
        maptype = maptype.name
    
    assert maptype is not None, f"maptype is neither MapType nor str"
    maptype = maptype.lower()
    
    returned_maps = siibra.find_maps(parcellation_id, space_id, maptype=maptype, extra_spec=extra_spec)
    
    if len(returned_maps) == 0:
        raise NotFound(f"get_map with spec {parcellation_id!r}, {space_id!r}, {maptype!r}, {extra_spec!r} found no map.")
    return instance_to_model(returned_maps[0], detail=True).dict()

@data_decorator(ROLE)
def statistical_map_nii_gz(parcellation_id: str, region_id: str, space_id: str, extra_spec: str="", *, no_cache: bool=False):
    filename, return_cached, warningtext = cache_region_statistic_map(parcellation_id, region_id, space_id, extra_spec, no_cache=no_cache)
    return filename, return_cached

@data_decorator(ROLE)
def statistical_map_info_json(parcellation_id: str, region_id: str, space_id: str, extra_spec: str="", *, no_cache: bool=False):
    filename, return_cached, warningtext = cache_region_statistic_map(parcellation_id, region_id, space_id, extra_spec, no_cache=no_cache)

    import nibabel as nib
    import numpy as np
    nii = nib.load(filename)
    data = nii.get_fdata()
    return {
        "min": np.min(data),
        "max": np.max(data),
    }

@data_decorator(ROLE)
def labelled_map_nii_gz(parcellation_id: str, space_id: str, region_id: str=None):
    """Retrieve and save labelled map / regional mask (if necessary), and then return the path of the map.

    Args:
        parcellation_id: lookup id of the parcellation of the map
        region_id: lookup id of the region of the map
        space_id: lookup id of the space of the map
    
    Returns:
        path to labelled map/regional mask, if a cached file is returned
    """
    
    full_filename, return_cached, warningtext = cache_parcellation_labelled_map(parcellation_id, space_id, region_id)
    return full_filename, return_cached

@data_decorator(ROLE)
def resampled_template(parcellation_id: str, space_id: str):
    full_filename, return_cached, warningtext = cache_resampled_map(parcellation_id, space_id)
    return full_filename, return_cached

@register_warmup_fn()
def warmup_maps():
    import siibra
    from siibra.atlases.sparsemap import SparseMap
    from siibra.atlases.parcellationmap import Map
    smaps: List[SparseMap] = siibra.find_maps(maptype="statistical")
    for map in smaps:
        try:
            map._get_readable_sparseindex(warmup=True)
        except Exception as e:
            logger.warning(f"Failed to save sparseindex: {str(e)}")
        try:
            instance_to_model(map, detail=True)
        except Exception as e:
            logger.warning(f"map {map.space_id=!r} {map.parcellation_id=!r} instance to model {str(e)}")
    
    maps: List[Map] = siibra.find_maps(maptype="labelled")

    def try_instance_to_model(m: Map):
        logger.info(f"Caching map {map.space_id=!r} {map.parcellation_id=!r}")
        try:
            return instance_to_model(m, detail=True)
        except Exception as e:
            logger.warning(f"map {map.space_id=!r} {map.parcellation_id=!r} instance to model {str(e)}")

    all_maps = [*smaps, *maps]
    for mp in all_maps:
        try_instance_to_model(mp)

